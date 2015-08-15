#!flask/bin/python
import os, time
import sys
import string
import random
import pwd
import subprocess
from dateutil.parser import parse
from flask import Flask, jsonify, abort, make_response
from flask_httpauth import HTTPBasicAuth
from werkzeug.contrib.cache import SimpleCache

#Get config variables
try:
	hostname = os.environ['API_HOST']
	portnumber = os.environ['API_PORT']
	key = os.environ['API_KEY']
except KeyError, e:
	sys.exit("Failed initialize environment variables: please set " + str(e))

	
#Init app
app = Flask(__name__)
auth = HTTPBasicAuth()
cache = SimpleCache()


#Authentication
@auth.get_password
def get_password(username):
	if username == 'key':
		return key
	return None


#Error handlers:
@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'User not found'}), 404)

@app.errorhandler(422)
def unprocessable(error):
	return make_response(jsonify({'status': 'error', 'error': 'cannot create user'}), 422)


#Helping functions
def getFolderSize(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += getFolderSize(itempath)
    return total_size

def oldest_modification_date(folder):
	oldest_date = time.ctime(os.path.getmtime(min(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(folder)
        for filename in filenames),
        key=lambda fn: os.stat(fn).st_mtime)))
	dt = parse(oldest_date)
	return dt.strftime('%Y-%m-%dT%H:%M:%S%z')

def newest_modification_date(folder):
	newest_date = time.ctime(os.path.getmtime(max(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(folder)
        for filename in filenames),
        key=lambda fn: os.stat(fn).st_mtime)))
	dt = parse(newest_date)
	return dt.strftime('%Y-%m-%dT%H:%M:%S%z')


#Routes
@app.route('/accounts', methods=['GET'])
@auth.login_required
def listAccounts():
	while os.path.exists('./get_accounts.flag'):
		time.sleep(1)
	os.mknod('./get_accounts.flag')
	accounts = {}
	for p in pwd.getpwall():
		if '/home/' in p.pw_dir:
			account = cache.get(p.pw_name)
			if account is None:
				if os.path.isdir(p.pw_dir):
					account = {
								'username': p.pw_name,
							 	'file_count': sum([len(files) for r, d, files in os.walk(p.pw_dir)]),
							 	'total_file_size': int(getFolderSize(p.pw_dir)),
							 	'first_upload_date': oldest_modification_date(p.pw_dir),
							 	'last_upload_date': newest_modification_date(p.pw_dir),
							}
				else:
					account = {
					
								'username': p.pw_name,
								'error': 'Could not read data'
							
							}
				cache.set(p.pw_name, account, timeout = 2 * 60)
			accounts[p.pw_dir] = account
	os.remove('./get_accounts.flag')
	return jsonify({'accounts': accounts})

@app.route('/accounts/create', methods=['POST'])
@auth.login_required
def createUser():
	for i in range(5):
		try:
			username = 'user' + ''.join(random.choice(string.digits) for _ in range(5))
			pwd.getpwnam(username)
			continue
		except KeyError:
			password = ''.join(random.choice('0123456789abcdef') for _ in range (10))
			createUserCommand = 'useradd --home-dir /home/' + username + ' --create-home --no-user-group --shell /usr/bin/nologin --comment api ' + username
			setPasswordCommand = 'echo "' + username + ':' + password + '" | chpasswd'
			create_result = subprocess.call(createUserCommand, shell=True)
			set_password_result = subprocess.call(setPasswordCommand, shell=True)
			try:
				pwd.getpwnam(username)
				for p in pwd.getpwnam(username):
					account = {
							'username': username,
							'file_count': 0,
							'total_file_size': 0,
							'first_upload_date': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
							'last_upload_date': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
					}
				cache.set(username, account, timeout = 2 * 60)
				apiAnswer = [
					{
						'status': 'ok',
						'username': username,
						'password': password
					}
				]
			except KeyError:
				abort(422)

			return jsonify(apiAnswer[0])
	else:
		abort(422)

@app.route('/accounts/delete/<string:username>', methods=['POST'])
@auth.login_required
def deleteUser(username):
	try:
		pwd.getpwnam(username)
		removeUserCommand = 'userdel -r ' + username
		remove_result = subprocess.call(removeUserCommand, shell=True)
		apiAnswer = [
						{
							'status': 'ok'
						}
				]
		cache.delete(username)
		return jsonify(apiAnswer[0])
	except KeyError:
		abort(404)


@app.route('/accounts/resetpassword/<string:username>', methods=['POST'])
@auth.login_required
def resetPasswordFor(username):
	try:
		pwd.getpwnam(username)
		password = ''.join(random.choice('0123456789abcdef') for _ in range (10))
		setPasswordCommand = 'echo "' + username + ':' + password + '" | chpasswd'
		set_password_result = subprocess.call(setPasswordCommand, shell=True)
		apiAnswer = [
					{
						'status': 'ok',
						'username': username,
						'password': password
					}
				]
		return jsonify(apiAnswer[0])
	except KeyError:
		abort(404)


#Start app
if __name__ == '__main__':
	app.run(debug=True, host=hostname, port=int(portnumber))
