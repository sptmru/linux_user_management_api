#!flask/bin/python
import string
import random
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/accounts/create', methods=['POST'])
def get_answer():
	username = 'user' + ''.join(random.choice(string.digits) for _ in range(5))
	return username;

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
