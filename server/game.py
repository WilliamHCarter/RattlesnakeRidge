from server.scenes import Scene_t, UserInput_t, test_scene, test_scene_two, GameData
from server.response import Response, LastMessage, MessageResponse, OptionResponse
from agents.conversation import LLM_t, PlayerAgent
import yaml


class Session:
    scene_stack: list[Scene_t] = [
        test_scene,
        test_scene_two,
    ]
    last_response = None

    def __init__(self, llm: LLM_t, prompts, setting):
        self.llm = llm
        self.player = PlayerAgent()
        self.prompts = prompts
        self.setting = setting

        self.start_next_scene()

    @property
    def game_data(self):
        return GameData(
            llm=self.llm,
            actors=[],
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
        return len(self.scene_stack) == 0 and self.current_scene is None

    def play(self, user_input: str) -> Response:
        if self.is_gameover():
            return LastMessage("The game is over.")

        if not self.scene_started:
            if user_input is not None:
                print(f'[WARN] Got user input "{user_input}" at the beginning of a scene. This is unexpected.')
            resp = next(self.current_scene)
            self.scene_started = True
        else:
            resp = self.current_scene.send(user_input)

        if isinstance(resp, LastMessage):
            self.start_next_scene()

        self.last_response = resp
        return resp

    def is_input_valid(self, user_input: UserInput_t) -> bool:
        """Check that the user input is valid given the last response sent."""
        if self.last_response is None: return True
        match self.last_response:
            case MessageResponse():
                # Any message is good
                return True
            case OptionResponse():
                # Only if the response is one of the options
                return user_input in self.last_response.choices
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

    prompts = load_dict("data/prompts.yaml")
    setting = load_dict("data/setting.yaml")

    return Session(
        llm=llm,
        prompts=prompts,
        setting=setting
    )


def play_game(session: Session, user_input: str) -> Response:
    return session.play(user_input)
