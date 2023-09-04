from dotenv import load_dotenv
import os

load_dotenv()

#For local builds, go to .env.template file and follow directions.
api_key = os.environ.get('LLM_API_KEY')