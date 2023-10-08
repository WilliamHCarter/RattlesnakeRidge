import os
from flask import Flask
from flask_session import Session

app = Flask(__name__)

# Access environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

from app import routes
