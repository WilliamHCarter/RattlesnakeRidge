from dataclasses import dataclass
from copy import copy


@dataclass(frozen=True)
class GenericMessageResponse:
    """
    Could add other fields here in the future to further decorate the frontend.
    For example: font color, font size, character write speed (instead of it all appearing at once?)
    """
    message: str
    # Options for t-y-p-i-n-g out message, one character at a time.
    do_type_message: bool = False
    character_delay_ms: int = 30

@dataclass(frozen=True)
class LastMessage(GenericMessageResponse):
    pass

@dataclass(frozen=True)
class MessageResponse(GenericMessageResponse):
    pass

@dataclass(frozen=True)
class NumberResponse(GenericMessageResponse):
    pass

@dataclass(frozen=True)
class OptionResponse(GenericMessageResponse):
    options: list[str] = None

@dataclass(frozen=True)
class MessageDelay(GenericMessageResponse):
    delay_ms: int = 1000

# For the gunshot
@dataclass(frozen=True)
class SoundDelay:
    sound_name: str
    delay_ms: int

Response = LastMessage | MessageResponse | NumberResponse | MessageDelay | OptionResponse | SoundDelay


def marshal_response(r: Response) -> dict:
    data = copy(r.__dict__)
    data["type"] = r.__class__.__name__
    return data


def unmarshal_response(r: dict) -> Response:
    raise NotImplementedError()


if __name__ == '__main__':
    print(f"We have {len(Response.__args__)} different response types:")
    for a in Response.__args__:
        print('-', a.__name__)

    examples = [
        LastMessage("This is a final message for a scene"),
        MessageResponse("This is a message that also requests a response"),
        NumberResponse("This is a message that requests a number response"),
        MessageDelay("This is a message with a built-in delay", 1337),
        OptionResponse("This is a message with a list of options for the end user to choose from",
                       ["Option 1", "Other option"]),
        SoundDelay("sound_file_name.mp3", 1337)
    ]

    for ex in examples:
        print(f"\nExample of {ex.__class__.__name__}:")
        print(marshal_response(ex))
