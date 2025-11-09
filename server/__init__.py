# pyright: reportImportCycles=false
import logging

logger = logging.getLogger(__name__)

# Global app variable that will be set by create_app
app = None

def create_app():
    """Create and configure Flask app"""
    global app
    import os
    from flask import Flask
    from flask_cors import CORS
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_session import Session

    app = Flask(__name__)

    # Access environment variables
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SESSION_TYPE"] = "filesystem"

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

    # Import routes after app creation to avoid circular imports
    import server.routes  # noqa: F401

    return app
