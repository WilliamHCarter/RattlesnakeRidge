from time import sleep

from server.game import initialize_game, play_game
from server.commands import *

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a console logger
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)


def sleep(delay: float):
    pass


def text_input() -> str:
    return input("You:  ")


def print_rich(command: Command):
    assert(isinstance(command, GenericMessageCommand))
    if command.do_type_message:
        delay = command.character_delay_ms / 1000.0
        for c in command.message:
            print(c, end='', flush=True)
            sleep(delay)
        print()
    else:
        print(command.message)


def local_implementation(incoming_command) -> None | str:
    match incoming_command:
        case SceneEndCommand():
            print_rich(incoming_command)
            sleep(1)
            print("\n\n", end='')
            return None
        case MessageCommand():
            print_rich(incoming_command)
            return text_input()
        case MessageDelayCommand():
            print_rich(incoming_command)
            sleep(incoming_command.delay_ms / 1000)
            return None
        case SelectOptionCommand():
            print_rich(incoming_command)
            for (choice, details) in incoming_command.options:
                print(f" - {choice}: {details}")
            inp = text_input()
            while inp not in incoming_command.choices:
                print("You must select one of the options.")
                inp = text_input()
            return inp
        case SoundDelayCommand():
            print(f'~!#&^#%)~~ {incoming_command.sound_name} ~~(%&!&*@#!')
            sleep(incoming_command.delay_ms / 1000)
            return None


if __name__ == "__main__":
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

    game = initialize_game(llm=llm)
    user_response = None
    while not game.is_gameover():
        response = play_game(game, user_response)
        user_response = local_implementation(response)
        assert game.is_input_valid(user_response)
