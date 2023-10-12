from server.scenes import Scene_t, UserInput_t, test_scene, test_scene_two
from server.response import Response, LastMessage, MessageResponse, NumberResponse, OptionResponse


# Todo:: all of the AI stuff lol.
class Session:
    scene_stack: list[Scene_t] = [
        test_scene,
        test_scene_two,
    ]
    last_response = None

    def __init__(self):
        self.start_next_scene()

    def start_next_scene(self) -> bool:
        if len(self.scene_stack) == 0: 
            self.current_scene = None
            return False
        next_scene = self.scene_stack[0]
        self.scene_stack = self.scene_stack[1:]
        self.current_scene = next_scene()
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
        if self.last_response is None: return False
        match self.last_response:
            case MessageResponse():
                # Any message is good
                return True
            case NumberResponse():
                # Only if this can become a number
                try:
                    int(user_input)
                    return True
                except:
                    return False
            case OptionResponse():
                # Only if the response is one of the options
                return user_input in self.last_response.choices
        return True


def initialize_game() -> Session:
    return Session()


def play(session: Session, user_input: str) -> Response:
    return session.play(user_input)
