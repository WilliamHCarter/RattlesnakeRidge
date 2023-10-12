from time import sleep

from server.game import initialize_game, play
from server.response import *

def local_scene_executor(scene_func):
    send_message_to_player = print
    wait_for_player_number_input = input
    wait_for_player_text_input = lambda: input("You: ")

    # Start the scene
    scene = scene_func()
    scene_response = next(scene)

    while True:
        match scene_response:
            case LastMessage():
                send_message_to_player(scene_response.message)
                return
            case MessageResponse():
                send_message_to_player(scene_response.message)
                response = wait_for_player_text_input()
                scene_response = scene.send(response)
            case NumberResponse():
                send_message_to_player(scene_response.message)
                response = int(wait_for_player_number_input())
                scene_response = scene.send(response)
            case MessageDelay():
                send_message_to_player(scene_response.message)
                sleep(scene_response.delay_ms / 1000)
                scene_response = next(scene)


def text_input() -> str:
    return input("You:  ")


def number_input() -> int:
    inp = input()
    while True:
        try:
            return int(inp)
        except:
            inp = input("Expected number. Try again: ")


def local_response_implementation(scene_response) -> None | str:
    match scene_response:
        case LastMessage():
            print(scene_response.message)
            return None
        case MessageResponse():
            print(scene_response.message)
            return text_input()
        case NumberResponse():
            print(scene_response.message)
            return number_input()
        case MessageDelay():
            print(scene_response.message)
            sleep(scene_response.delay_ms / 1000)
            return None
        case OptionResponse():
            print(scene_response.message)
            for option in scene_response.options:
                print("-", option)
            inp = text_input()
            while inp not in scene_response.options:
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
        response = play(game, user_response)
        # print(">>>>>", response)
        user_response = local_response_implementation(response)
