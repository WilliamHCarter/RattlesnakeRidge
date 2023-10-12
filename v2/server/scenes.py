from server.response import *
from collections.abc import Callable


Scene_t = Callable[[], Response]


# Dummy method, improve later.
def get_agent_response(_):
    return "Wow... very cool..."


def test_scene() -> Response:
    yield MessageDelay("This is the scene intro...", 1000)

    # Select an agent to speak with
    selection = yield NumberResponse("Choose an agent (1-4) to speak with")
    while selection not in list(range(1,4+1)):
        selection = yield NumberResponse("Bad selection. Choose an agent to speak with")

    # Begin a conversation after a short intro
    yield MessageDelay("After a long hike up a hill or something, you see that dude you were supposed to talk with...", 1000)

    # Have a conversation
    messages_left = 4
    user_input = "First time"
    while messages_left > 0:
        response = f"Dude: {get_agent_response(user_input)}"
        if messages_left > 1:
            user_input = yield MessageResponse(response)
        else:
            yield MessageDelay(response, 300)
        messages_left -= 1

    # Example of some more scripting here with the other options
    yield MessageDelay("Your conversation is over, and the scene is finished.", 3000)
    yield MessageDelay("Wait... who is that over there?!", 1500)
    yield SoundDelay("gunshot.mp3", 2000)
    yield MessageDelay("Oh no! That dude is now bleeding out! Someone shot them!", 1200)
    choice = yield OptionResponse("Quick! What to do!",
                         [
                             "Help dude",
                             "Hunt"
                         ])
    if choice == "Help dude":
        yield MessageDelay("You quickly bandage them up and save their life. Good job!", 2400)
    else:
        yield MessageDelay("You try to hunt down the shooter, but they got away!", 2400)

    yield LastMessage("The scene is finished fr this time.")