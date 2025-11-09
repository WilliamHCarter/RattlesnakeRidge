import logging
from typing import Any

import yaml

import server.scenes.rattlesnake_ridge
from server.agents.conversation import Agent, LLM_t, PlayerAgent
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

    def __init__(self, llm: LLM_t, prompts, setting, actors):
        self.llm = llm
        self.player = PlayerAgent()
        self.prompts = prompts
        self.setting = setting
        self.actors = actors
        self.logs = []
        self.gameover = False

        self.start_next_scene()

    @property
    def game_data(self):
        return GameData(
            llm=self.llm,
            actors=self.actors,
            prompts=self.prompts,
            player=self.player,
            setting_data=self.setting,
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
        logger.info(f"*** SESSION.PLAY CALLED *** user_input='{user_input}', scene_started={self.scene_started}")
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
                logger.info(f"*** SESSION.PLAY: GETTING FIRST COMMAND FROM SCENE ***")
                resp = next(self.current_scene)
                logger.info(f"*** SESSION.PLAY: GOT FIRST COMMAND: {type(resp).__name__} ***")
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
                logger.info(f"*** SESSION.PLAY: SENDING USER INPUT TO SCENE: '{user_input}' ***")
                resp = self.current_scene.send(user_input)
                logger.info(f"*** SESSION.PLAY: GOT RESPONSE COMMAND: {type(resp).__name__} ***")
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


def initialize_game(llm: LLM_t) -> Session:
    data_dir = "server/data/"

    prompts = load_dict(data_dir + "prompts.yaml")
    setting = load_dict(data_dir + "setting.yaml")

    # Create the actors
    character_names = ["flint", "billy", "clara", "whistle"]
    actors = [
        Agent(datafile=data_dir + f"characters/{name}.yaml") for name in character_names
    ]

    logger.info("Initialized a new game")
    return Session(llm=llm, prompts=prompts, setting=setting, actors=actors)


def play_game(session: Session, user_input: str | None) -> Command:
    logger.info(f"*** PLAY_GAME CALLED *** user_input='{user_input}'")
    result = session.play(user_input)
    logger.info(f"*** PLAY_GAME RETURNING {type(result).__name__} ***")
    return result
