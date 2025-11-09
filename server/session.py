import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Global in-memory game state storage for active sessions
game_states = {}

# API usage tracking
ai_api_usage: int = 0
AI_API_LIMIT: int = 30
last_reset_date = datetime.now().date()  # Initialize with the current date


def check_and_reset_limit():
    """Check if the current date is different from the last reset date and reset usage if needed."""
    global ai_api_usage, last_reset_date
    # Check if the current date is different from the last reset date
    if datetime.now().date() > last_reset_date:
        # Reset the usage and update the last reset date
        ai_api_usage = 0
        last_reset_date = datetime.now().date()
        logger.info("API usage limit reset for new day")