from copy import copy
from dotenv import load_dotenv
import os
import yaml
from agents.agent import Agent, PlayerAgent
from test_scenes import intro_scene


def load_dict(filename: str) -> dict:
    with open(filename, 'r') as file:
        raw = file.read()
    return yaml.safe_load(raw)

#===== Setup the env and chat model =====#
prompts = load_dict('data/prompts.yaml')
setting = load_dict('data/setting.yaml')
load_dotenv()

#For local builds, go to .env.template file and follow directions.
api_key = os.environ.get('LLM_API_KEY')
model = 'gpt-3.5-turbo'

intro_scene(prompts, setting)



