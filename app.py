#!flask/bin/python
import os, time
import sys
import string
import random
import pwd
from dateutil.parser import parse
from flask import Flask, json, abort, make_response
from flask_httpauth import HTTPBasicAuth

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
app.config["JSON_SORT_KEY"] = False


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

@app.errorhandler(422)
def unprocessable(error):
	return make_response(jsonify({'status': 'error', 'error': 'cannot generate proper username'}), 422)

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


#Routes:
@app.route('/accounts', methods=['GET'])
@auth.login_required
def listAccounts():
	data = []
	for p in pwd.getpwall():
		if '/home/' in p.pw_dir:
			if os.path.isdir(p.pw_dir):
				d = [
						p.pw_dir,
						{
							'username': p.pw_name,
						 	'file_count': sum([len(files) for r, d, files in os.walk(p.pw_dir)]),
						 	'total_file_size': int(getFolderSize(p.pw_dir)),
						 	'first_upload_date': oldest_modification_date(p.pw_dir),
						 	'last_upload_date': newest_modification_date(p.pw_dir)
						}
					]
				data.append(d)
			else:
				d = [
						p.pw_dir, 
						{
							'username': p.pw_name,
							'error': 'Could not read data'
						}
					]
				data.append(d)

	return json.dumps(data)

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
			createUserCommand = 'useradd --home-dir /home/' + username + ' --create-home --no-user-group --gid 5000 --shell /usr/bin/nologin --comment api ' + username
			setPasswordCommand = 'echo "' + username + ':' + password + '" | chpasswd'
			apiAnswer = [
				{
					'status': 'ok',
					'username': username,
					'password': password
				}
			]
			return jsonify(apiAnswer[0])
	else:
		abort(422)

@app.route('/accounts/delete/<string:username>', methods=['POST'])
@auth.login_required
def deleteUser(username):
	return "Under Construction"

@app.route('/accounts/resetpassword/<string:username>', methods=['POST'])
@auth.login_required
def resetPasswordFor(username):
	return "Under Construction"


#Start app
if __name__ == '__main__':
	app.run(debug=True, host=hostname, port=int(portnumber))
