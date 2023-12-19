import os
import logging
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Access environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'

# Global in-memory game state storage for active sessions
game_states = {}

# Define allowed origins based on the environment
if os.environ.get('FLASK_ENV') == 'development':
    origins = "http://localhost:5173"
else:
    origins = "https://stories.williamcarter.dev"

CORS(app, origins=[origins])

# Initialize Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10000 per hour"]
)
limiter.init_app(app)

Session(app)

from server import routes
