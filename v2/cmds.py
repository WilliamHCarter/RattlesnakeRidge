from dataclasses import dataclass

@dataclass(frozen=True)
class LastMessage:
    message: str

@dataclass(frozen=True)
class MessageResponse:
    message: str

@dataclass(frozen=True)
class NumberResponse:
    message: str

@dataclass(frozen=True)
class MessageDelay:
    message: str
    delay_ms: int

Response = LastMessage | MessageResponse | NumberResponse | MessageDelay


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
            yield MessageDelay(response, 3000)
        messages_left -= 1

    yield LastMessage("Your conversation is over, and the scene is finished.")

from time import sleep
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


if __name__ == "__main__":
    local_scene_executor(test_scene)
