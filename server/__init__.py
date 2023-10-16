import os
import logging

logger = logging.getLogger(__name__)

from flask import Flask
from flask_session import Session
from flask_cors import CORS

app = Flask(__name__)

# Access environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

#Global in-memory game state storage for active sessions
game_states = {}

# Define allowed origins based on the environment
if os.environ.get('FLASK_ENV') == 'development':
    origins = "http://localhost:5173"
else:
    origins = "placeholder"

CORS(app, origins=[origins])


Session(app)

from server import routes
