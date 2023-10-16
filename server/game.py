from server import logger
from server.scenes import *
from server.commands import Command, SceneEndCommand, MessageCommand, SelectOptionCommand
from server.agents.conversation import LLM_t, PlayerAgent, Agent
import yaml


class Session:
    scene_stack: list[Scene_t] = [
        first_day_scene,
        first_night_scene,
        second_day_morning_scene,
        second_day_afternoon_scene,
        final_confrontation_scene
    ]
    last_scene_output : Command | None = None

    def __init__(self, llm: LLM_t, prompts, setting, actors):
        self.llm = llm
        self.player = PlayerAgent()
        self.prompts = prompts
        self.setting = setting
        self.actors = actors

        self.gameover = False

        self.start_next_scene()

    @property
    def game_data(self):
        return GameData(
            llm=self.llm,
            actors=self.actors,
            prompts=self.prompts,
            player=self.player,
            setting_data=self.setting
        )

    def start_next_scene(self) -> bool:
        if len(self.scene_stack) == 0: 
            self.current_scene = None
            return False
        next_scene = self.scene_stack[0]
        self.scene_stack = self.scene_stack[1:]
        self.current_scene = next_scene(self.game_data)
        self.scene_started = False

    def is_gameover(self) -> bool:
        return self.gameover

    def play(self, user_input: str) -> Command:
        if self.is_gameover():
            logger.warn("User attempted to play a game that has finished")
            return SceneEndCommand("The game is over.")

        if not self.scene_started:
            if user_input is not None:
                logger.warn("got user input \"%s\" at the beginning of a scene. Expected `None` input.", user_input)
            try:
                resp = next(self.current_scene)
            except Exception as error:
                logger.error("failed to get the next command from current scene. error: %s", error)
                self.gameover = True
                raise error
            self.scene_started = True
        else:
            try:
                resp = self.current_scene.send(user_input)
            except Exception as error:
                logger.error("failed to get the next command from current scene. error: %s", error)
                self.gameover = True
                raise error

        if isinstance(resp, SceneEndCommand):
            self.start_next_scene()

        if resp.is_game_over: 
            logger.info("game has ended")
            self.gameover = True

        self.last_scene_output = resp
        return resp

    def is_input_valid(self, user_input: UserInput_t) -> bool:
        """Check that the user input is valid given the last command sent."""
        if self.last_scene_output is None: return True
        match self.last_scene_output:
            case MessageCommand():
                # Any message is good
                return True
            case SelectOptionCommand():
                # Only if the user response is one of the choices
                return user_input in self.last_scene_output.choices
        return True


def load_dict(filename: str) -> dict:
    with open(filename, "r") as file:
        raw = file.read()
    return yaml.safe_load(raw)


def initialize_game(llm: LLM_t = None) -> Session:
    # If we didn't give an llm, use the fake list chat model for now.
    # In the future, we'll require an LLM to be provided here, but I
    # don't want to break anything right now
    # todo:: update.
    if llm is None:
        from langchain.chat_models import FakeListChatModel
        llm = FakeListChatModel(
            verbose=True,
            responses=[
                    "Hi there, I'm talking to you.",
                    "This is a response",
                    "I say something else too!",
                    "Ok, goodbye now!",
                ],
            )

    data_dir = "server/data/"

    prompts = load_dict(data_dir + "prompts.yaml")
    setting = load_dict(data_dir + "setting.yaml")

    # Create the actors
    character_names = ["flint", "billy", "clara", "whistle"]
    actors = [
        Agent(datafile=data_dir + f"characters/{name}.yaml") for name in character_names
    ]

    logger.info("Initialized a new game")
    return Session(
        llm=llm,
        prompts=prompts,
        setting=setting,
        actors=actors
    )


def play_game(session: Session, user_input: str) -> Command:
    return session.play(user_input)
