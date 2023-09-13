from copy import copy
from dotenv import load_dotenv
import os
import yaml
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from agents.agent import Agent, PlayerAgent
from test_scenes import test_select_scene, test_multiagent_scene
from scenes import first_day_intro, first_night_cutscene, second_day_intro

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

# Set the Model
llm = FakeListChatModel(
    verbose=True, 
    responses=[f"Hi there, I'm talking to you.", 'That is not nice', '[QUIT] This conversation is over.']
)
#llm = ChatOpenAI(openai_api_key=api_key, model=model)

#===== Setup the agents =====#
# Dummy name haha
character_names = ['flint', 'billy', 'clara', 'whistle']

agents = [Agent(datafile=f'data/characters/{name}.yaml') for name in character_names]
player = PlayerAgent(datafile='data/characters/player.yaml')

#===== Run Each Story Scene =====#
#test_select_scene(llm, prompts, setting, agents, player)
#multiagent_scene(llm, prompts, setting, agents, player)
#first_day_intro(llm, prompts, setting, agents, player)
#first_night_cutscene()
second_day_intro(llm, prompts, setting, agents, player)



