#!flask/bin/python
import os
import sys
import string
import random
import pwd
from flask import Flask, jsonify, abort, make_response
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


#Routes:
@app.route('/accounts', methods=['GET'])
@auth.login_required
def listAccounts():
	return "Under Construction"

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
