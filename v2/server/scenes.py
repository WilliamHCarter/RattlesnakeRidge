from server.response import *
from collections.abc import Callable
from typing import Generator
from copy import copy
# from agents.conversation import Conversation


UserInput_t = str | int | None
SceneReturn_t = Generator[Response, UserInput_t, None]
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


def test_scene() -> SceneReturn_t:
    yield MessageDelay("This is the scene intro...", delay_ms=1000)

    # Select an agent to speak with
    options=[
        ("1", "Marshal Flint"),
        ("2", "Clara"),
    ]
    selection = yield OptionResponse("Choose a person to speak with", options=options)
    yield MessageDelay(f"You chose to meet with {options[int(selection) - 1][1]}!", delay_ms = 700)

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
                             ("1", "Help dude"),
                             ("2", "Hunt")
                         ])
    if choice == "1":
        yield MessageDelay("You quickly bandage them up and save their life. Good job!", delay_ms=2400)
    else:
        yield MessageDelay("You try to hunt down the shooter, but they got away!", delay_ms=2400)

    yield LastMessage("The scene is finished fr this time.")


def test_scene_two() -> SceneReturn_t:
    yield MessageDelay("\n\nThis is a second test scene", delay_ms=700)
    yield MessageDelay("It doesn't have anything interesting, just showing it works", delay_ms=300, do_type_message=True)
    yield MessageDelay("Custom text speed", delay_ms=600, do_type_message=True, character_delay_ms=60)
    yield LastMessage("Goodbye!")


FIRST_DAY_INTRO = """As the sun sets on the horizon, you ride into the dusty outpost 
of Rattlesnake Ridge. The villagers are gathered around the town 
center, murmuring about a heinous crime: a local prospector named Jeb, 
known for recently striking gold, has been found dead. Word is that 
his stash of gold is missing too. You decide to step in, and after 
introducing yourself, you have the option to speak to the main 
suspects: Whistle, Miss Clara, Marshal Flint, and Billy "Snake Eyes" 
Thompson.
"""

# def first_day_scene(actors, player, llm_data) -> SceneReturn_t:
#     yield MessageDelay(FIRST_DAY_INTRO)

#     remaining_actors = copy(actors)
#     number_actors = len(remaining_actors)

#     # Talk to every actor
#     for _ in range(number_actors):
#         # Choose an actor
#         if len(remaining_actors) > 1:
#             choice = yield OptionResponse(
#                 message = "Who would you like to talk to?",
#                 options = [
#                     (str(i+1), actor.name + " -- " + actor.short_description) 
#                     for i, actor in enumerate(remaining_actors)
#                 ])
                
#             index = int(choice) - 1
#         else:
#             index = 0

#         selected_actor = remaining_actors[index]
#         remaining_actors.remove(selected_actor)

#         # Tell the user who they're talking to
#         yield MessageDelay(f"Time to talk to {selected_actor.name}")
#         yield MessageDelay(selected_actor.introduction, delay_ms=3200)
        
#         # Have the conversation
#         agent_order = (
#             [selected_actor, player]
#         )

#         conversation = Conversation(agent_order, llm_data)

#         responses_left = 6
#         message = "[Enters the room]"
#         while responses_left > 0:
#             responses = conversation.converse(message)
#             for i, r in enumerate(responses):
#                 if r.conversation_ends: responses_left = 0
#                 if i < len(responses) - 1 or responses_left == 0:
#                     yield MessageDelay(r.text)
#                 else:
#                     message = yield MessageResponse(r.text)
#             responses_left -= 1
        
#         if len(remaining_actors) > 0:
#             yield MessageDelay("It's getting late in the day, and you have more people to meet...")

#     yield MessageDelay("You've had a long and arduous journey; time to go to bed for the night.")
