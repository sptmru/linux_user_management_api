# Simple Linux user management API

# Installation
Virtualenv, python-dev and pip should be installed on the server.
(for Debian-based systems: apt-get install python-pip python-virtualenv python-dev)

virtualenv flask
flask/bin/pip install flask
flask/bin/pip install python-dateutil
flask/bin/pip install Flask-HttpAuth
flask/bin/pip install Flask-Cache

export API_HOST="0.0.0.0"
export API_PORT="5000"
export API_KEY="keystring"

chmod +x ./app.py
./app.py

Basic auth credentials: 
username - key
password - API_KEY

### Contacts
In case of any questions please contact me on Elance (https://www.elance.com/s/supporteam/), on Skype (supporteam.ru) or by email (me@supporteam.ru).

