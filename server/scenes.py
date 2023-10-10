from copy import copy
from dataclasses import dataclass
from agents.conversation import Conversation, ConversationResponse, LLMData
from agents.agent import Agent, PlayerAgent


# ================ Helper Functions ===================#
@dataclass
class SceneState:
    def __init__(self):
        self.step: int = 0
        self.selected_agent: Agent = None


def validate_input(input_message: str, valid_inputs: list[int]):
    if input_message.isdigit():
        number = int(input_message)
        if number in valid_inputs:
            return number
        else:
            return "Number is out of range!"
    else:
        return "Invalid input. Please enter a number!"


# ================ Scene Functions ===================#


def first_day_intro(agents: list[Agent], player: PlayerAgent, llm_data: LLMData):
    remaining_intro = copy(agents)
    print(
        """
\n As the sun sets on the horizon, you ride into the dusty outpost 
of Rattlesnake Ridge. The villagers are gathered around the town 
center, murmuring about a heinous crime: a local prospector named Jeb, 
known for recently striking gold, has been found dead. Word is that 
his stash of gold is missing too. You decide to step in, and after 
introducing yourself, you have the option to speak to the main 
suspects: Whistle, Miss Clara, Marshal Flint, and Billy "Snake Eyes" 
Thompson. \n
        """
    )
    for _ in range(4):
        # Select a person to talk to
        if len(remaining_intro) > 1:
            print("Who would you like to talk to?")
            for i, agent in enumerate(remaining_intro):
                print(f"{str(i+1)}: {agent.name} -- {agent.short_description}")
            input_range = range(1, len(remaining_intro) + 1)
            in_message = "Enter a number (1-" + str(len(input_range)) + "): "
            selection = validate_input(in_message, input_range) - 1
            selected_agent = remaining_intro[selection]
        else:
            selected_agent = remaining_intro[0]
            print(f"\nTime to talk to {selected_agent.name}\n")

        remaining_intro.remove(selected_agent)

        # Print the introduction for this character
        print(selected_agent.introduction, "\n")

        # Have a simple time-bounded conversation
        agent_order = (
            [selected_agent, player]
            if selected_agent.does_talk_first_on_first_meeting
            else [player, selected_agent]
        )
        conversation = Conversation(agent_order, llm_data)

        responses_left = 6
        while responses_left > 0:
            # Poke the AI if it speaks first, else we deal with the player and skip to AI
            if agent_order == [selected_agent, player] and responses_left == 6:
                message = "[Enters the room]"
            else:
                message = input(f"{player.name}: ")
            # Normal response conversation and message printing
            responses: list[ConversationResponse] = conversation.converse(message)
            for i, r in enumerate(responses):
                if r.text:
                    print(f"{r.agent}: {r.text}")
                if r.conversation_ends:
                    responses_left = 0

            responses_left -= 1

        print("\nThe conversation has ended.\n")


def first_night_cutscene():
    print(
        """
The moon is high when a piercing scream echoes through the night. 
Everyone rushes out to find Whistle's Saloon in disarray -- a scuffle 
has occurred. You notice a bloodied poker card on the floor, the ace 
of spades. This might be a clue, but to what?
        """
    )


def second_day_intro(agents: list[Agent], player: PlayerAgent, llm_data: LLMData):
    print(
        """ 
Sunlight reveals tense faces. The townfolk have formed two groups.
On one side, by the water trough, stands Whistle, looking ruffled, 
and Miss Clara, her comforting hand on his arm. They seem to be
arguing with the other group, consisting of Marshal Flint and
Billy, who are on the steps of the Marshal's Office. You need
to make a choice quickly: which duo will you approach to get
their side of the story?
        """
    )

    print("Who would you like to talk to?\n")
    print("1: Billy and Clara")
    print("2: Flint and Whistle\n")
    b_and_c: list[Agent] = [
        agent
        for agent in agents
        if agent.name in ['Billy "Snake Eyes" Thompson', "Miss Clara"]
    ]
    f_and_w: list[Agent] = [
        agent for agent in agents if agent.name in ["Marshal Flint", "Whistle"]
    ]

    input_range = range(1, len(b_and_c) + 1)
    in_message = "Enter a number (1-" + str(len(input_range)) + "): "
    selection = validate_input(in_message, input_range) - 1
    agent_order: list[Agent] = b_and_c if selection == 0 else f_and_w

    # Another time-bound convo
    responses_left = 12
    conversation = Conversation(agent_order + [player], llm_data)

    while responses_left > 0:
        # DO THIS BETTER?, this pokes the AI if it speaks first, else we deal with the player and skip to AI
        if responses_left == 6:
            message = "[Enters the room]"
        else:
            message = input(f"{player.name}: ")
        # Normal response conversation and message printing
        responses: list[ConversationResponse] = conversation.converse(message)
        for i, r in enumerate(responses):
            if r.text:
                print(f"{r.agent}: {r.text}")
            if r.conversation_ends:
                responses_left = 0

        responses_left -= 1

    print(
        """
A sudden gunshot rings out, interrupting your conversation. The 
townsfolk scatter, heading to their homes or businesses to seek cover.
        """
    )


def second_day_afternoon(
    state: SceneState,
    agents: list[Agent],
    player: PlayerAgent,
    llm_data: LLMData,
    user_input: str,
):
    match state.step:
        # Scene intro and character select
        case 0:
            state.step += 1
            return {
                "message": "The town is quieter now, and the townspeople's nerves are on edge. You have the chance to speak to one more person in-depth. Who would you like to talk to?",
                "options": [
                    f"{i+1}: {agent.name} -- {agent.short_description}"
                    for i, agent in enumerate(agents)
                ],
            }

        # Selection Confirmation
        case 1:
            selection = validate_input(user_input, [1, 2, 3, 4])
            if selection is not int:
                return {"message": selection}
            state.selected_agent = agents[selection - 1]
            state.step += 1
            return {
                "message": f"Time to talk to {state.selected_agent.name}.",
            }

        # Conversation steps
        case _ if 2 <= state.step <= 7:
            agent_order = [player, state.selected_agent]
            conversation = Conversation(agent_order, llm_data)
            responses = conversation.converse(user_input)
            response_texts = [f"{r.agent}: {r.text}" for r in responses if r.text]

            if any(r.conversation_ends for r in responses):
                state.step = 8
                response_texts.append("The conversation has ended.")
            else:
                state.step += 1

            return {"messages": response_texts}

        case 8:
            return {"message": "Scene completed."}

        case _:
            raise Exception("Invalid step")


def final_confrontation(agents: list[Agent], player: PlayerAgent, llm_data: LLMData):
    print(
        """
Night has fallen. You gather everyone in the Saloon, where the mood is 
palpable. Shadows dance on the walls as you stand before the suspects. 
Here, you must make your case to the townfolk, after which you must 
aim your gun and pulling the trigger on the character you believe to 
be the killer.
        """
    )

    responses_left = 12
    conversation = Conversation([player] + agents, llm_data)

    while responses_left > 0:
        print("You have ", responses_left, " statements left.\n")
        message = input(f"{player.name}: ")
        # Normal response conversation and message printing
        responses: list[ConversationResponse] = conversation.converse(message)
        for i, r in enumerate(responses):
            if r.text:
                print(f"{r.agent}: {r.text}")
            # Todo:: for the final confrontation, we should not let the agents make the
            # conversation end early. Instead, they should be allowed to 'exit' the
            # conversation by refusing to say anything more.
            if r.conversation_ends:
                responses_left = 0

        responses_left -= 1

    # Select a person to eliminate
    print("\n\nWho is your final target?\n")
    for i, agent in enumerate(agents):
        print(f"{str(i+1)}: {agent.name} -- {agent.short_description}")
    selection = int(input(f"\nEnter a number (1-4): ")) - 1
    print()
    selected_agent = agents[selection]

    # Agents speaks their last words
    final = conversation.speak_directly(
        "You've been shot by the player, speak your dying words given your played experience",
        selected_agent,
    )
    for i, r in enumerate(final):
        if r.text:
            print(f"{r.agent}: {r.text}")
    if selected_agent.name == "Whistle":
        print(
            """
You aim your gun at Whistle, and pull the trigger. The bullet
flies through the air, and hits Whistle square in the chest. He
falls to the ground, dead. The townsfolk cheer, and you are
hailed as a hero. The ghost of Jeb can rest easy.
        """
        )
    else:
        print(
            f"""
As {selected_agent.name} crumples to the ground, chaos ensues. 
The real killer takes advantage of the confusion, locking you up 
in the Marshal's Office with accusations of murder, while they 
make their escape, leaving you with the weight of your misjudgment.
            """,
        )

    print(
        """
    Thanks For Playing Rattlesnake Ridge!
    Made by Will Carter and Aidan McHugh
        """
    )
