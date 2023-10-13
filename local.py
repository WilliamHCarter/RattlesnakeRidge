from time import sleep

from server.game import initialize_game, play_game
from server.response import *


def text_input() -> str:
    return input("You:  ")


def print_rich(r: Response):
    assert(isinstance(r, GenericMessageResponse))
    if r.do_type_message:
        delay = r.character_delay_ms / 1000.0
        for c in r.message:
            print(c, end='', flush=True)
            sleep(delay)
        print()
    else:
        print(r.message)


def local_response_implementation(scene_response) -> None | str:
    match scene_response:
        case LastMessage():
            print_rich(scene_response)
            sleep(1)
            return None
        case MessageResponse():
            print_rich(scene_response)
            return text_input()
        case MessageDelay():
            print_rich(scene_response)
            sleep(scene_response.delay_ms / 1000)
            return None
        case OptionResponse():
            print_rich(scene_response)
            for (choice, details) in scene_response.options:
                print(f" - {choice}: {details}")
            inp = text_input()
            while inp not in scene_response.choices:
                print("You must select one of the options.")
                inp = text_input()
            return inp
        case SoundDelay():
            print(f'~!#&^#%)~~ {scene_response.sound_name} ~~(%&!&*@#!')
            sleep(scene_response.delay_ms / 1000)
            return None


if __name__ == "__main__":
    game = initialize_game()
    user_response = None
    while not game.is_gameover():
        response = play_game(game, user_response)
        user_response = local_response_implementation(response)
        assert game.is_input_valid(user_response)