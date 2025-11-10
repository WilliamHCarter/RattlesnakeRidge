import logging
import yaml
import server.scenes.rattlesnake_ridge

from typing import Any
from openai import OpenAI
from server.clue_randomizer import ClueRandomizer, inject_scenario_into_agents, MurderScenario

from server.agents.conversation import Agent, LLMData, PlayerAgent
from server.commands import (
    Command,
    MessageCommand,
    SceneEndCommand,
    SelectOptionCommand,
    marshal_command,
)
from server.scenes import *
from server.scenes.core import GameData, Scene_t, UserInput_t

logger = logging.getLogger(__name__)


class Session:
    scene_stack: list[Scene_t] = server.scenes.rattlesnake_ridge.SCENE_ORDER
    last_scene_output: Command | None = None

    def __init__(self, llm_data: LLMData, prompts, setting, actors, murder_scenario):
        self.llm_data = llm_data
        self.player = PlayerAgent()
        self.prompts = prompts
        self.setting = setting
        self.actors = actors
        self.murder_scenario = murder_scenario
        self.logs = []
        self.gameover = False

        self.start_next_scene()

    @property
    def game_data(self):
        return GameData(
            llm_data=self.llm_data,
            actors=self.actors,
            prompts=self.prompts,
            player=self.player,
            setting_data=self.setting,
            murder_scenario=self.murder_scenario,
        )

    def start_next_scene(self) -> bool:
        if len(self.scene_stack) == 0:
            self.current_scene = None
            return False
        next_scene = self.scene_stack[0]
        self.scene_stack = self.scene_stack[1:]
        self.current_scene = next_scene(self.game_data)
        self.scene_started = False
        return True

    def is_gameover(self) -> bool:
        return self.gameover

    def play(self, user_input: str | None) -> Command:
        if self.is_gameover():
            logger.warn("User attempted to play a game that has finished")
            return SceneEndCommand("The game is over.", is_game_over=True)

        if not self.scene_started:
            if user_input is not None and user_input != "":
                logger.warn(
                    'got user input "%s" at the beginning of a scene. Expected `None` input.',
                    user_input,
                )
            try:
                assert self.current_scene is not None
                resp = next(self.current_scene)
            except Exception as error:
                logger.error(
                    "failed to get the next command from current scene. error: %s",
                    error,
                )
                self.gameover = True
                raise error
            self.scene_started = True
        else:
            try:
                assert self.current_scene is not None
                resp = self.current_scene.send(user_input)
            except Exception as error:
                logger.error(
                    "failed to get the next command from current scene. error: %s",
                    error,
                )
                self.gameover = True
                raise error

        if isinstance(resp, SceneEndCommand):
            self.start_next_scene()

        if resp.is_game_over:
            logger.info("game has ended")
            self.gameover = True

        self.last_scene_output = resp
        if user_input != "":
            self.logs.append(marshal_command(MessageCommand(f"You: {user_input}")))
        self.logs.append(marshal_command(resp))
        return resp

    def is_input_valid(self, user_input: UserInput_t) -> bool:
        """Check that the user input is valid given the last command sent."""
        if self.last_scene_output is None:
            return True
        match self.last_scene_output:
            case MessageCommand():
                # Any message is good
                return True
            case SelectOptionCommand():
                # Only if the user response is one of the choices
                return user_input in self.last_scene_output.choices
        return True


def load_dict(filename: str) -> dict[str, Any]:
    with open(filename, "r") as file:
        raw = file.read()
    return yaml.safe_load(raw)


def initialize_game(llm_data: LLMData) -> Session:
    data_dir = "server/data/"

    prompts = load_dict(data_dir + "prompts.yaml")
    setting = load_dict(data_dir + "setting.yaml")

    # Create the actors
    character_names = ["flint", "billy", "clara", "whistle"]
    actors = [
        Agent(datafile=data_dir + f"characters/{name}.yaml") for name in character_names
    ]

    # Generate random murder scenario
    randomizer = ClueRandomizer(clue_bank_path=data_dir + "clue_bank.yaml")
    murder_scenario = randomizer.generate_scenario()

    # Inject scenario into agents (modifies agents and prompts)
    inject_scenario_into_agents(actors, murder_scenario, prompts)

    logger.info(f"Initialized a new game - Killer: {murder_scenario.killer}, Motive: {murder_scenario.motive}")
    return Session(llm_data=llm_data, prompts=prompts, setting=setting, actors=actors, murder_scenario=murder_scenario)


def play_game(session: Session, user_input: str | None) -> Command:
    return session.play(user_input)
