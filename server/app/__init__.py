import os
from flask import Flask
from flask_session import Session

app = Flask(__name__)

# Access environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

#Global in-memory game state storage for active sessions
game_states = {}

Session(app)

from app import routes
