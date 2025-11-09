# pyright: reportImportCycles=false
import logging
import os
from datetime import datetime

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Access environment variables
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"

# Global in-memory game state storage for active sessions
game_states = {}
ai_api_usage: int = 0
AI_API_LIMIT: int = 30
last_reset_date = datetime.now().date()  # Initialize with the current date


def check_and_reset_limit(self):
    # Check if the current date is different from the last reset date
    if datetime.now().date() > self.last_reset_date:
        # Reset the usage and update the last reset date
        API_USAGE = 0
        last_reset_date = datetime.now().date()


# Define allowed origins based on the environment
if os.environ.get("FLASK_ENV") == "development":
    origins = "http://localhost:5173"
else:
    origins = "https://stories.williamcarter.dev, https://api.stories.williamcarter.dev"

_ = CORS(app, origins=[origins])

# Initialize Flask-Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["10000 per hour"])
limiter.init_app(app)

_ = Session(app)

from server import routes  # noqa: F401, E402  # pyright: ignore[reportImportCycles]
