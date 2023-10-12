import server.scenes
from server.response import Response, LastMessage


# Todo:: all of the AI stuff lol.
class Session:
    scene_stack: list[server.scenes.Scene_t] = [
        server.scenes.test_scene,
        server.scenes.test_scene_two,
    ]

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
        return resp


def initialize_game() -> Session:
    return Session()


def play(session: Session, user_input: str) -> Response:
    return session.play(user_input)
