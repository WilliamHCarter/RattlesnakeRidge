from server.commands import *
from copy import copy
from server.agents.conversation import Agent
from server.scenes.core import *


def first_day_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelayCommand("""As the sun sets on the horizon, you ride into the dusty outpost \
of Rattlesnake Ridge. The villagers are gathered around the town \
center, murmuring about a heinous crime: a local prospector named Jeb, \
known for recently striking gold, has been found dead. Word is that \
his stash of gold is missing too. You decide to step in, and after \
introducing yourself, you have the option to speak to the main \
suspects: Whistle, Miss Clara, Marshal Flint, and Billy "Snake Eyes" \
Thompson.""")

    remaining_actors = copy(game_data.actors)
    number_actors = len(remaining_actors)

    # Talk to every actor
    for _ in range(number_actors):
        # Choose an actor
        if len(remaining_actors) > 1:
            choice = yield SelectOptionCommand(
                message="Who would you like to talk to?",
                options=[
                    (str(i + 1), actor.name + " -- " + actor.short_description)
                    for i, actor in enumerate(remaining_actors)
                ],
            )

            assert choice is not None
            index = int(choice) - 1
        else:
            index = 0

        selected_actor = remaining_actors[index]
        remaining_actors.remove(selected_actor)

        # Tell the user who they're talking to
        yield MessageDelayCommand(f"Time to talk to {selected_actor.name}\n")
        yield MessageDelayCommand(selected_actor.introduction + "\n", delay_ms=3200)

        # Have the conversation
        conversation = make_conversation(game_data, [selected_actor, game_data.player])
        yield from have_conversation(conversation, 1)

        if len(remaining_actors) > 0:
            yield MessageDelayCommand(
                "It's getting late in the day, and you have more people to meet...\n"
            )

    yield SceneEndCommand(
        "\nYou've had a long and arduous journey; time to go to bed for the night."
    )


def first_night_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelayCommand(
        "The moon is high when a piercing scream echoes through the night. Everyone rushes out to find Whistle's Saloon in disarray -- a scuffle has occurred. You notice a bloodied poker card on the floor, the ace of spades. This might be a clue, but to what?",
        delay_ms=6000,
    )
    yield SceneEndCommand(
        "You attempt to rest some more, but are too nervous to get any real sleep. You lay in your cot until sunrise."
    )


def second_day_morning_scene(game_data: GameData) -> SceneReturn_t:
    intro = "Sunlight reveals tense faces. The townfolk have formed two groups. On one side, by the water trough, stands Whistle, looking ruffled,  and Miss Clara, her comforting hand on his arm. They seem to be arguing with the other group, consisting of Marshal Flint and Billy, who are on the steps of the Marshal's Office. You need to make a choice quickly: which duo will you approach to get their side of the story?'\n"
    yield MessageDelayCommand(intro, delay_ms=6000)

    # Choose between Billy and Clara vs Flint and Whistle
    options = [("1", "Billy and Clara"), ("2", "Flint and Whistle")]
    choice = yield SelectOptionCommand(
        "Who would you like to talk to?", options=options
    )
    assert choice is not None

    # Get the list of participants in this conversation
    names = (
        ['Billy "Snake Eyes" Thompson', "Miss Clara"]
        if choice == "1"
        else ["Marshal Flint", "Whistle"]
    )
    actors: list[Agent] = [agent for agent in game_data.actors if agent.name in names]
    # Add the player
    actors += [game_data.player]

    # Have a conversation
    conversation = make_conversation(game_data, actors)
    yield from have_conversation(conversation, 1)

    yield SceneEndCommand(
        """\nA sudden gunshot rings out, interrupting your conversation. The \
townsfolk scatter, heading to their homes or businesses to seek cover."""
    )


def second_day_afternoon_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelayCommand(
        "The town is quieter now and the townspeople's nerves are on edge. You have the chance to speak to one more person in-depth."
    )

    options = [(str(i + 1), actor.name) for (i, actor) in enumerate(game_data.actors)]
    choice = yield SelectOptionCommand(
        "Who would you like to speak with?", options=options
    )
    assert choice is not None
    index = int(choice) - 1
    selected = game_data.actors[index]

    yield MessageDelayCommand(
        f"\nYou approach {selected.name} for a final conversation.\n"
    )

    yield from have_conversation(
        make_conversation(game_data, [selected, game_data.player]), 6
    )

    yield SceneEndCommand(
        "Night has fallen. The townsfolk demand an answer. You send out word for all the suspects to gather in the Saloon."
    )


def final_confrontation_scene(game_data: GameData) -> SceneReturn_t:
    yield MessageDelayCommand(
        "The mood is palpable as you enter the Saloon. Shadows dance on the walls as you stand before the suspects. Here, you must make your case to the townfolk, after which you must aim your gun and pulling the trigger on the character you believe to be the killer."
    )

    conv = copy(game_data.actors) + [game_data.player]
    conversation = make_conversation(game_data, conv)

    responses_left = 1
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
            yield MessageDelayCommand(msg)

        if responses_left > 1:
            message = yield MessageCommand(
                f"\nYou have {responses_left - 1} statements left."
            )
            responses = conversation.converse(message)
            # Adds an empty line
            yield MessageDelayCommand("", delay_ms=0)

        responses_left -= 1

    # Time for the final decision
    yield MessageDelayCommand("\n\nThe time has come to make a final decision\n")
    yield MessageDelayCommand(
        "Who do you kill?\n", character_delay_ms=90, do_type_message=True
    )

    options = [(str(i + 1), actor.name) for (i, actor) in enumerate(game_data.actors)]
    choice = yield SelectOptionCommand("Pick.", options=options)
    index = int(choice) - 1
    selected = game_data.actors[index]

    # Check if the player got it right using the murder scenario
    if hasattr(game_data, 'murder_scenario') and game_data.murder_scenario:
        is_correct = game_data.murder_scenario.is_correct_guess(selected.name)
    else:
        # Fallback to original hardcoded solution if no scenario
        is_correct = selected.name == "Whistle"

    if is_correct:
        yield MessageDelayCommand(
            f"\n\nYou aim your gun at {selected.name}, and pull the trigger."
        )
        yield SoundDelayCommand("bang.mp3", delay_ms=1000)
        yield MessageDelayCommand(
            f"The bullet flies through the air, and hits {selected.name} square in the chest."
        )
        yield MessageDelayCommand(
            f"{selected.name} falls to the ground. As they take their last breath, they confess: 'Yes... I killed Rusty... because of {game_data.murder_scenario.motive}...' The townsfolk cheer; you are hailed as a hero. The ghost of Rusty can rest easy."
        )
    else:
        yield MessageDelayCommand(
            "\n\nYou pull the trigger", do_type_message=False, delay_ms=300
        )

        last_words = conversation.speak_directly(
            "You've been shot by the player, speak your dying words given your played experience",
            selected,
        )[0].text

        yield MessageDelayCommand(f"{selected.name}: {last_words}")

        yield MessageDelayCommand(
            f"""\nAs {selected.name} crumples to the ground, chaos ensues. \
The real killer takes advantage of the confusion, locking you up \
in the Marshal's Office with accusations of murder, while they \
make their escape, leaving you with the weight of your misjudgment.""",
        )

    yield MessageDelayCommand("\n", delay_ms=3000)
    yield MessageDelayCommand("Thank you for playing Rattlesnake Ridge!")
    yield SceneEndCommand(
        "Made with pride by Will Carter and Aidan McHugh", is_game_over=True
    )



SCENE_ORDER = [
    first_day_scene,
    first_night_scene,
    second_day_morning_scene,
    second_day_afternoon_scene,
    final_confrontation_scene,
]
