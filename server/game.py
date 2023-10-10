import os
import yaml
from dotenv import load_dotenv
from dataclasses import dataclass
from agents.conversation import LLMData
from agents.agent import Agent, PlayerAgent
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from flask import session
from server.scenes import (
    SceneState,
    first_day_intro,
    first_night_cutscene,
    second_day_intro,
    second_day_afternoon,
    final_confrontation,
)

# A mapping of scene names to scene functions
SCENES = {
    "first_day_intro": first_day_intro,
    "first_night_cutscene": first_night_cutscene,
    "second_day_intro": second_day_intro,
    "second_day_afternoon": second_day_afternoon,
    "final_confrontation": final_confrontation,
}


@dataclass
class GameState:
    scene_state: SceneState
    agents: list[Agent | PlayerAgent]
    player: PlayerAgent
    current_scene: str
    llm_data: LLMData


def initialize_game() -> GameState:
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
    llm_data: LLMData = LLMData(
        llm, prompts["single_person_conversation_complex"], setting
    )

    # ===== Setup the agents =====#
    character_names = ["flint", "billy", "clara", "whistle"]

    agents = [
        Agent(datafile=f"data/characters/{name}.yaml") for name in character_names
    ]
    player = PlayerAgent(datafile="data/characters/player.yaml")

    return GameState(
        agents=agents,
        player=player,
        current_scene="second_day_afternoon",
        llm_data=llm_data,
        scene_state=SceneState(),
    )


def play(gs: GameState, user_input: str):
    # Get the current scene from the game state
    response = SCENES[gs.current_scene](
        gs.scene_state, gs.agents, gs.player, gs.llm_data, user_input
    )
    if response:
        return response
    # Handle the case where the scene is not found
    return "System Error, scene not found"
