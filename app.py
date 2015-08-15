#!flask/bin/python
import os
import string
import random
import pwd
from flask import Flask, jsonify, abort, make_response

app = Flask(__name__)

@app.errorhandler(422)
def unprocessable(error):
	return make_response(jsonify({'status': 'error', 'error': 'cannot generate proper username'}), 422)

@app.route('/accounts/create', methods=['POST'])
def get_answer():
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





if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
