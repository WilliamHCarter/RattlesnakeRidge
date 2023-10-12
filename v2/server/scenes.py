from server.response import *
from collections.abc import Callable


Scene_t = Callable[[], Response]


# Dummy method, improve later.
agent_responses = [
    "Hello there!",
    "I'm fine, how are you?",
    "Good to hear.",
    "Goodbye!"
]
response_num = 0
def get_agent_response(user_message: str | None) -> str:
    global response_num
    resp = agent_responses[response_num]
    response_num += 1
    return resp


def test_scene() -> Response:
    yield MessageDelay("This is the scene intro...", delay_ms=1000)

    # Select an agent to speak with
    selection = yield NumberResponse("Choose an agent (1-4) to speak with")
    while selection not in list(range(1,4+1)):
        selection = yield NumberResponse("Bad selection. Choose an agent to speak with")

    # Begin a conversation after a short intro
    yield MessageDelay("After a long hike up a hill or something, you see that dude you were supposed to talk with...", delay_ms=1000)

    # Have a conversation
    messages_left = 4
    user_input = "First time"
    while messages_left > 0:
        response = f"Dude: {get_agent_response(user_input)}"
        if messages_left > 1:
            user_input = yield MessageResponse(response)
        else:
            yield MessageDelay(response, delay_ms=300)
        messages_left -= 1

    # Example of some more scripting here with the other options
    yield MessageDelay("Your conversation is over, and the scene is finished.", delay_ms=3000)
    yield MessageDelay("Wait... who is that over there?!", do_type_message=True, delay_ms=1500)
    yield SoundDelay("gunshot.mp3", 2000)
    yield MessageDelay("Oh no! That dude is now bleeding out! Someone shot them!", delay_ms=1200)
    choice = yield OptionResponse("Quick! What to do!",
                         options = [
                             "Help dude",
                             "Hunt"
                         ])
    if choice == "Help dude":
        yield MessageDelay("You quickly bandage them up and save their life. Good job!", delay_ms=2400)
    else:
        yield MessageDelay("You try to hunt down the shooter, but they got away!", delay_ms=2400)

    yield LastMessage("The scene is finished fr this time.")


def test_scene_two() -> Response:
    yield MessageDelay("\n\nThis is a second test scene", delay_ms=700)
    yield MessageDelay("It doesn't have anything interesting, just showing it works", delay_ms=300, do_type_message=True)
    yield MessageDelay("Custom text speed", delay_ms=600, do_type_message=True, character_delay_ms=60)
    yield LastMessage("Goodbye!")
