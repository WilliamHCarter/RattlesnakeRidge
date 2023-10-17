from dataclasses import dataclass, KW_ONLY, field
from copy import copy


@dataclass(frozen=True, kw_only=True)
class Command:
    is_game_over: bool = False
    expects_user_input: bool = field(default=False, init=False)


@dataclass(frozen=True)
class GenericMessageCommand(Command):
    """
    Could add other fields here in the future to further decorate the frontend.
    For example: font color, font size, character write speed (instead of it all appearing at once?)
    """
    message: str
    # All following fields are optional
    _: KW_ONLY
    # Options for t-y-p-i-n-g out message, one character at a time.
    do_type_message: bool = False
    character_delay_ms: int = 30

@dataclass(frozen=True)
class SceneEndCommand(GenericMessageCommand):
    pass

@dataclass(frozen=True)
class MessageCommand(GenericMessageCommand):
    expects_user_input = True

@dataclass(frozen=True)
class SelectOptionCommand(GenericMessageCommand):
    options: list[tuple[str, str]] = None
    expects_user_input = True
    @property
    def choices(self):
        return [x[0] for x in self.options]

@dataclass(frozen=True)
class MessageDelayCommand(GenericMessageCommand):
    delay_ms: int = 1000

# For the gunshot
@dataclass(frozen=True)
class SoundDelayCommand(Command):
    sound_name: str
    delay_ms: int

Commands = SoundDelayCommand | MessageDelayCommand | SelectOptionCommand | MessageCommand | SceneEndCommand


def marshal_command(command: Command) -> dict:
    data = copy(command.__dict__)
    # Include the expects_user_input field explicitly as it may be otherwise optimized out
    data["expects_user_input"] = command.expects_user_input
    data["type"] = command.__class__.__name__
    return data


def unmarshal_command(_: dict) -> Command:
    raise NotImplementedError()


if __name__ == '__main__':
    print(f"We have {len(Commands.__args__)} different command types:")
    for a in Commands.__args__:
        print('-', a.__name__)

    examples = [
        SceneEndCommand("This is a final message for a scene"),
        MessageCommand("This is a message that also requests a response from the user"),
        MessageDelayCommand("This is a message with a built-in delay", delay_ms=1337),
        SelectOptionCommand("This is a message with a list of options for the end user to choose from",
                       options=[
                           ("1", "Option 1"),
                           ("2", "Other option")
                       ]),
        SoundDelayCommand("sound_file_name.mp3", delay_ms=1337)
    ]

    for ex in examples:
        print(f"\nExample of {ex.__class__.__name__}:")
        print(marshal_command(ex))
