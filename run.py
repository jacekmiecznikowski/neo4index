from app import app
import os

app.secret_key = os.urandom(24)

if __name__ == '__main__':
	app.run(debug=True)	

# FLASK_APP=run.py FLASK_DEBUG=1 flask run