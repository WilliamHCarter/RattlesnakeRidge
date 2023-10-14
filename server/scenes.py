from server.response import *
from collections.abc import Callable
from typing import Generator
from copy import copy
from server.agents.conversation import LLM_t, Conversation, Agent, LLMData, PlayerAgent


@dataclass(frozen=True)
class GameData:
    llm: LLM_t
    actors: list[Agent]
    player: PlayerAgent
    prompts: dict[str, str]
    setting_data: dict[str, str]


UserInput_t = str | int | None
SceneReturn_t = Generator[Response, UserInput_t, None]
Scene_t = Callable[[GameData], Response]


def make_conversation(
            game_data: GameData, 
            order: list[Agent], 
            prompt_name: str = "single_person_conversation_complex"
        ) -> Conversation:
    llm_data = LLMData(
        game_data.llm, 
        game_data.prompts[prompt_name], 
        game_data.setting_data
    )
    return Conversation(order, llm_data)


def have_conversation(conversation: Conversation, max_player_messages: int):
    responses_left = max_player_messages

    responses = conversation.begin_conversation()

    while responses_left > 0:
        # Display all the responses
        for i, r in enumerate(responses):
            if r.conversation_ends: responses_left = 0
            msg = f"{r.agent}: {r.text}"
            if i < len(responses) - 1 or responses_left == 0:
                yield MessageDelay(msg)
            else:
                # If this is the last response and the player has allowed messages,
                # get input and get new responses
                message = yield MessageResponse(msg)
                responses = conversation.converse(message)

        responses_left -= 1


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


def test_scene(game_data: GameData) -> SceneReturn_t:
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
    dummy_agent = Agent("data/characters/billy.yaml")
    conversation = make_conversation(game_data, [dummy_agent, game_data.player])

    messages_left = 4
    user_input = "First time"
    while messages_left > 0:
        # Prompt the 'LLM'
        actor_response = conversation.converse(user_input)
        assert len(actor_response) == 1
        actor_response = actor_response[0]

        # Format
        response = f"Dude: {actor_response.text}"

        # Display
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


def test_scene_two(game_data: GameData) -> SceneReturn_t:
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

def first_day_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelay(FIRST_DAY_INTRO)

    remaining_actors = copy(game_data.actors)
    number_actors = len(remaining_actors)

    # Talk to every actor
    for _ in range(number_actors):
        # Choose an actor
        if len(remaining_actors) > 1:
            choice = yield OptionResponse(
                message = "Who would you like to talk to?",
                options = [
                    (str(i+1), actor.name + " -- " + actor.short_description) 
                    for i, actor in enumerate(remaining_actors)
                ])
                
            index = int(choice) - 1
        else:
            index = 0

        selected_actor = remaining_actors[index]
        remaining_actors.remove(selected_actor)

        # Tell the user who they're talking to
        yield MessageDelay(f"Time to talk to {selected_actor.name}\n")
        yield MessageDelay(selected_actor.introduction + '\n', delay_ms=3200)
        
        # Have the conversation
        conversation = make_conversation(game_data, [selected_actor, game_data.player])
        yield from have_conversation(conversation, 6) 
        
        if len(remaining_actors) > 0:
            yield MessageDelay("It's getting late in the day, and you have more people to meet...\n")

    yield LastMessage("\nYou've had a long and arduous journey; time to go to bed for the night.")


def first_night_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelay("The moon is high when a piercing scream echoes through the night. Everyone rushes out to find Whistle's Saloon in disarray -- a scuffle has occurred. You notice a bloodied poker card on the floor, the ace of spades. This might be a clue, but to what?", delay_ms=6000)
    yield LastMessage("You attempt to rest some more, but are too nervous to get any real sleep. You lay in your cot until sunrise.")


def second_day_morning_scene(game_data: GameData) -> SceneReturn_t:
    intro = "Sunlight reveals tense faces. The townfolk have formed two groups. On one side, by the water trough, stands Whistle, looking ruffled,  and Miss Clara, her comforting hand on his arm. They seem to be arguing with the other group, consisting of Marshal Flint and Billy, who are on the steps of the Marshal's Office. You need to make a choice quickly: which duo will you approach to get their side of the story?'\n"
    yield MessageDelay(intro, delay_ms=6000)

    # Choose between Billy and Clara vs Flint and Whistle
    options = [
        ("1", "Billy and Clara"),
        ("2", "Flint and Whistle")
    ]
    choice = yield OptionResponse("Who would you like to talk to?", options=options)

    # Get the list of participants in this conversation
    names = ['Billy "Snake Eyes" Thompson', "Miss Clara"] if choice == "1" else ["Marshal Flint", "Whistle"]
    actors: list[Agent] = [
        agent
        for agent in game_data.actors
        if agent.name in names
    ]
    # Add the player
    actors += [game_data.player]

    # Have a conversation
    conversation = make_conversation(game_data, actors)
    yield from have_conversation(conversation, 12) 

    yield LastMessage(
        """\nA sudden gunshot rings out, interrupting your conversation. The \
townsfolk scatter, heading to their homes or businesses to seek cover."""
    )


def second_day_afternoon_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelay("The town is quieter now and the townspeople's nerves are on edge. You have the chance to speak to one more person in-depth.")

    options = [(str(i+1), actor.name) for (i, actor) in enumerate(game_data.actors)]
    choice = yield OptionResponse("Who would you like to speak with?",
                         options=options)
    index = int(choice) - 1
    selected = game_data.actors[index]

    yield MessageDelay(f"\nYou approach {selected.name} for a final conversation.\n")

    yield from have_conversation(make_conversation(game_data, [selected, game_data.player]), 6)

    yield LastMessage("Night has fallen. The townsfolk demand an answer. You send out word for all the suspects to gather in the Saloon.")


def final_confrontation_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelay("The mood is palpable as you enter the Saloon. Shadows dance on the walls as you stand before the suspects. Here, you must make your case to the townfolk, after which you must aim your gun and pulling the trigger on the character you believe to be the killer.")

    conv = copy(game_data.actors) + [game_data.player]
    conversation = make_conversation(game_data, conv)

    responses_left = 12
    responses = conversation.begin_conversation()

    while responses_left > 0:
        # Display all the responses
        for r in responses:
            # Not allowed here.
            # Todo:: for the final confrontation, we should not let the agents make the
            # conversation end early. Instead, they should be allowed to 'exit' the
            # conversation by refusing to say anything more.
            # if r.conversation_ends: responses_left = 0

            msg = f"{r.agent}: {r.text}"
            yield MessageDelay(msg)
        
        if responses_left > 1:
            message = yield MessageResponse(f"\nYou have {responses_left} statements left.")
            responses = conversation.converse(message)
            # Adds an empty line
            yield MessageDelay("", delay_ms=0)

        responses_left -= 1

    # Time for the final decision
    yield MessageDelay("\n\nThe time has come to make a final decision\n")
    yield MessageDelay("Who do you kill.\n", character_delay_ms=90, do_type_message=True)

    options = [(str(i+1), actor.name) for (i, actor) in enumerate(game_data.actors)]
    choice = yield OptionResponse("Pick.", options=options)
    index = int(choice) - 1
    selected = game_data.actors[index]

    if selected.name == "Whistle":
        yield MessageDelay("\n\nYou aim your gun at Whistle, and pull the trigger.")
        yield SoundDelay("bang.mp3", delay_ms=1000)
        yield MessageDelay("The bullet flies through the air, and hits Whistle square in the chest." )
        yield MessageDelay("Whistle falls to the ground, dead. The townsfolk cheer; you are hailed as a hero. The ghost of Jeb can rest easy.")
    else:
        yield MessageDelay("\n\nYou pull the trigger", do_type_message=False, delay_ms=300)

        last_words = conversation.speak_directly(
            "You've been shot by the player, speak your dying words given your played experience",
            selected,
        )[0].text

        yield MessageDelay(f"{selected.name}: {last_words}")

        yield MessageDelay(f"""\nAs {selected.name} crumples to the ground, chaos ensues. \
The real killer takes advantage of the confusion, locking you up \
in the Marshal's Office with accusations of murder, while they \
make their escape, leaving you with the weight of your misjudgment.""",)

    yield MessageDelay("\n", delay_ms=3000)
    yield MessageDelay("Thank you for playing Rattlesnake Ridge!")
    yield MessageDelay("Made with pride by Will Carter and Aidan McHugh")
    yield MessageDelay("Star our project on github")
    yield MessageDelay("hmu on linkedin ;)")
    yield LastMessage("And, scene.")

