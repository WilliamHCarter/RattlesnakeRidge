from copy import copy
from dataclasses import dataclass
from server.agents.conversation import Conversation, ConversationResponse, LLMData
from server.agents.agent import Agent, PlayerAgent


# ================ Data Classes ===================#
@dataclass
class SceneState:
    def __init__(self):
        self.step: int = 0
        self.selected_agent: Agent = None


@dataclass
class GameState:
    scene_state: SceneState
    agents: list[Agent | PlayerAgent]
    intro_agents: list[Agent]
    player: PlayerAgent
    current_scene: str
    llm_data: LLMData


# ================ Helper Functions ===================#
def validate_input(input_message: str, valid_inputs: list[int]):
    print(input_message)
    if input_message.isdigit():
        number = int(input_message)
        if number in valid_inputs:
            return number
        else:
            return "Number is out of range!"
    else:
        return "Invalid input. Please enter a number!"


def chat(gs: GameState, order: list[Agent | PlayerAgent], input: str, max_steps: int):
    conversation = Conversation(order, gs.llm_data)
    if order[0] != gs.player:
        input = "[Enters the room]"
    responses: list[ConversationResponse] = conversation.converse(input)
    response_texts = [f"{r.agent}: {r.text}" for r in responses if r.text]

    if any(r.conversation_ends for r in responses):
        gs.scene_state.step = max_steps
        response_texts.append("The conversation has ended.")
    else:
        gs.scene_state.step += 1

    return {"messages": response_texts}


# ================ Scene Functions ===================#


def first_day_intro(gs: GameState, state: SceneState, user_input: str):
    # Scene intro and character select
    intro_text = ""
    if state.step == 0:
        state.step += 1
        intro_text = 'As the sun sets on the horizon, you ride into the dusty outpost of Rattlesnake Ridge. The villagers are gathered around the town center, murmuring about a heinous crime: a local prospector named Jeb, known for recently striking gold, has been found dead. Word is that his stash of gold is missing too. You decide to step in, and after introducing yourself, you have the option to speak to the main suspects: Whistle, Miss Clara, Marshal Flint, and Billy "Snake Eyes" Thompson. \n\n'
    if gs.intro_agents:
        # Select a person to talk to
        if len(gs.intro_agents) > 1:
            if state.step == 1:
                state.step += 1
                return {
                    "message": intro_text + "Who would you like to talk to?",
                    "options": [
                        f"{i+1}: {agent.name} -- {agent.short_description}"
                        for i, agent in enumerate(gs.intro_agents)
                    ],
                    "system": "Enter a number (1-"
                    + str(range(1, len(gs.intro_agents)))
                    + "): ",
                }
            if state.step == 2:
                selection = validate_input(
                    user_input, list(range(1, len(gs.intro_agents) + 1))
                )
                if not isinstance(selection, int):
                    return {"message": selection}
                state.step += 1
                state.selected_agent = gs.intro_agents[selection - 1]

            if 3 <= state.step:
                agent_order = (
                    [state.selected_agent, gs.player]
                    if state.selected_agent.does_talk_first_on_first_meeting
                    else [gs.player, state.selected_agent]
                )
                responses = chat(gs, agent_order, user_input, 7)

                # Print the introduction for this character
                if state.step == 3:
                    responses["message"] = state.selected_agent.introduction

                if state.step > 6:
                    gs.intro_agents.remove(state.selected_agent)
                    state.step = 1

                return responses

        else:
            state.selected_agent = gs.intro_agents[0]
            if state.step == 1:
                intro_text = "\nTime to talk to " + state.selected_agent.name + "\n"

            responses = chat(gs, [state.selected_agent, gs.player], user_input, 7)
            if state.step > 6:
                gs.intro_agents.remove(state.selected_agent)
                state.step = 1
            return {"message": "" + intro_text, **responses}

    else:
        state.step = 0
        return "Scene completed."


def first_night_cutscene(gs: GameState, state: SceneState, user_input: str):
    if state.step == 0:
        state.step += 1
        return {
            "message": "The moon is high when a piercing scream echoes through the night. Everyone rushes out to find Whistle's Saloon in disarray -- a scuffle has occurred. You notice a bloodied poker card on the floor, the ace of spades. This might be a clue, but to what?"
        }
    if state.step == 1:
        state.step = 0
        return "Scene completed."


def second_day_intro(gs: GameState, state: SceneState, user_input: str):
    intro_text = ""
    if state.step == 0:
        state.step += 1
        intro_text = "Sunlight reveals tense faces. The townfolk have formed two groups. On one side, by the water trough, stands Whistle, looking ruffled,  and Miss Clara, her comforting hand on his arm. They seem to be arguing with the other group, consisting of Marshal Flint and Billy, who are on the steps of the Marshal's Office. You need to make a choice quickly: which duo will you approach to get their side of the story?'\n\n"

    if state.step == 1:
        state.step += 1
        return {
            "message": intro_text + "Who would you like to talk to?",
            "options": ["1: Billy and Clara", "2: Flint and Whistle"],
            "system": "Enter a number (1-2): ",
        }

    b_and_c: list[Agent] = [
        agent
        for agent in gs.agents
        if agent.name in ['Billy "Snake Eyes" Thompson', "Miss Clara"]
    ]
    f_and_w: list[Agent] = [
        agent for agent in gs.agents if agent.name in ["Marshal Flint", "Whistle"]
    ]

    selection = validate_input(user_input, [1, 2])
    if not isinstance(selection, int):
        return {"message": selection}
    agent_order: list[Agent] = b_and_c if (selection - 1) == 0 else f_and_w
    if state.step > 6:
        state.step = 100
        return {
            "message": "A sudden gunshot rings out, interrupting your conversation. The townsfolk scatter, heading to their homes or businesses to seek cover."
        }
    if state.step == 100:
        return "Scene completed."
    response = chat(gs, agent_order + [gs.player], user_input, 7)
    return response


def second_day_afternoon(gs: GameState, state: SceneState, user_input: str):
    match state.step:
        # Scene intro
        case 0:
            state.step += 1
            return {
                "message": "The town is quieter now, and the townspeople's nerves are on edge. You have the chance to speak to one more person in-depth. Who would you like to talk to?",
                "options": [
                    f"{i+1}: {agent.name} -- {agent.short_description}"
                    for i, agent in enumerate(gs.agents)
                ],
            }

        # Validate Agent Selection
        case 1:
            selection = validate_input(user_input, [1, 2, 3, 4])
            if not isinstance(selection, int):
                return {"message": selection}
            state.selected_agent = gs.agents[selection - 1]
            state.step += 1
            return {
                "message": f"Time to talk to {state.selected_agent.name}.",
            }

        # Have a Conversation
        case _ if 1 < state.step < 8:
            agent_order = [gs.player, state.selected_agent]
            response_texts = chat(gs, agent_order, user_input, 8)
            return {"messages": response_texts}

        case 8:
            state.step = 0
            return "Scene completed."

        case _:
            raise Exception("Invalid step")


def final_confrontation(gs: GameState, state: SceneState, user_input: str):
    if state.step == 0:
        state.step += 1
        return {
            "message": "Night has fallen. You gather everyone in the Saloon, where the mood is palpable. Shadows dance on the walls as you stand before the suspects. Here, you must make your case to the townfolk, after which you must aim your gun and pulling the trigger on the character you believe to be the killer."
        }
    if state.step < 12:
        responses_left = 12 - state.step
        responses = chat(gs, [gs.player] + gs.agents, user_input, 12)
        return {"message": "You have " + str(responses_left) + " statements left.\n", **responses}
    if state.step == 12:
        state.step += 1
        # Select a person to eliminate
        return {
            "message": "Who is your final target?",
            "options": [
                f"{i+1}: {agent.name} -- {agent.short_description}"
                for i, agent in enumerate(gs.agents)
            ],
            "system": "Enter a number (1-4): ",
        }
    if state.step == 13:
        selection = validate_input(user_input, [1, 2, 3, 4])
        selected_agent = gs.agents[selection - 1]

    # Agents speaks their last words
    conversation = Conversation([selected_agent], gs.llm_data)
    final = conversation.speak_directly(
        "You've been shot by the player, speak your dying words given your played experience",
        selected_agent,
    )
    for i, r in enumerate(final):
        if r.text:
            print(f"{r.agent}: {r.text}")
    if selected_agent.name == "Whistle":
        return {
            "message": "You aim your gun at Whistle, and pull the trigger. The bullet flies through the air, and hits Whistle square in the chest. He falls to the ground, dead. The townsfolk cheer, and you are hailed as a hero. The ghost of Jeb can rest easy."
        }
    else:
        return {
            "message": "As "
            + selected_agent.name
            + " crumples to the ground, chaos ensues. The real killer takes advantage of the confusion, locking you up in the Marshal's Office with accusations of murder, while they make their escape, leaving you with the weight of your misjudgment.",
            "system": "\n\nThanks For Playing Rattlesnake Ridge! \n Built by Will Carter and Aidan McHugh"
        }

