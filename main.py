from copy import copy
from dotenv import load_dotenv
import os
import yaml
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from agents.agent import Agent, PlayerAgent
from agents.conversation import LLMData
from test_scenes import test_select_scene, test_multiagent_scene
from local_scenes import (
    first_day_intro,
    first_night_cutscene,
    second_day_intro,
    second_day_afternoon,
    final_confrontation,
)


def load_dict(filename: str) -> dict:
    with open(filename, "r") as file:
        raw = file.read()
    return yaml.safe_load(raw)


# ===== Setup the env and chat model =====#
prompts = load_dict("data/prompts.yaml")
setting = load_dict("data/setting.yaml")
load_dotenv()

# For local builds, go to .env.template file and follow directions.
api_key = os.environ.get("LLM_API_KEY")
model = "gpt-3.5-turbo"

# Set the Model
llm = FakeListChatModel(
    verbose=True,
    responses=[
        f"Hi there, I'm talking to you.",
        "That is not nice",
        "[QUIT] This conversation is over.",
    ],
)
# llm = ChatOpenAI(openai_api_key=api_key, model=model)
llm_data: LLMData = LLMData(llm, prompts["single_person_conversation_complex"], setting)

# ===== Setup the agents =====#
character_names = ["flint", "billy", "clara", "whistle"]

agents = [Agent(datafile=f"data/characters/{name}.yaml") for name in character_names]
player = PlayerAgent(datafile="data/characters/player.yaml")


# ===== Run Each Story Scene =====#
first_day_intro(agents, player, llm_data)
first_night_cutscene()
second_day_intro(agents, player, llm_data)
second_day_afternoon(agents, player, llm_data)
final_confrontation(agents, player, llm_data)