from copy import copy
from agents.conversation import Conversation, ConversationResponse
from agents.agent import Agent, PlayerAgent

def first_day_intro(llm, prompts: dict, setting: dict, agents:list[Agent], player:PlayerAgent):
    
    remaining_intro = copy(agents)
    print("\nAs the sun sets on the horizon, you ride into the dusty outpost of Rattlesnake Ridge. The villagers are gathered around the town center, murmuring about a heinous crime: a local prospector named Jeb, known for recently striking gold, has been found dead. Word is that his stash of gold is missing too. You decide to step in, and after introducing yourself, you have the option to speak to the main suspects: Whistle, Miss Clara, Marshal Flint, and Billy \"Snake Eyes\" Thompson. \n")
    for _ in range(4):

        # Select a person to talk to
        if len(remaining_intro) > 1:
            print("Who would you like to talk to?")
            for i, agent in enumerate(remaining_intro):
                print(f'{str(i+1)}: {agent.name} -- {agent.short_description}')
            selection = int(input(f"Enter a number (1-{len(remaining_intro)}): ")) - 1
            print()
            selected_agent = remaining_intro[selection]
        else:
            selected_agent = remaining_intro[0]
            print(f'\nTime to talk to {selected_agent.name}\n')

        remaining_intro.remove(selected_agent)

        # Print the introduction for this character
        print(selected_agent.introduction, '\n')

        # Have a simple time-bounded conversation
        agent_order = [selected_agent, player] if selected_agent.does_talk_first_on_first_meeting else [player, selected_agent]
        conversation = Conversation(agent_order, prompts['single_person_conversation_complex'], setting, llm)
        responses_left = 6
        while responses_left > 0:
            #Poke the AI if it speaks first, else we deal with the player and skip to AI
            if agent_order == [selected_agent, player] and responses_left == 6:
                message = '[Enters the room]'
            else:
                message = input(f'{player.name}: ')
            #Normal response conversation and message printing 
            responses: list[ConversationResponse] = conversation.converse(message)
            for i, r in enumerate(responses):
                if r.text: print(f'{r.agent}: {r.text}')
                if r.conversation_ends: responses_left = 0

            responses_left -= 1

        print("\nThe conversation has ended.\n")

def first_night_cutscene():
    print("The moon is high when a piercing scream echoes through the night. Everyone rushes out to find Whistle's Saloon in disarray – a scuffle has occurred. You notice a bloodied poker card on the floor, the ace of spades. This might be a clue, but to what? \n")

def second_day_intro(llm, prompts: dict, setting: dict, agents:list[Agent], player:PlayerAgent):
    print("Sunlight reveals tense faces. The townfolk have formed two groups. On one side, by the water trough, stands Whistle, looking ruffled, and Miss Clara, her comforting hand on his arm. They seem to be arguing with the other group, consisting of Marshal Flint and Billy, who are on the steps of the Marshal's Office. You need to make a choice quickly: which duo will you approach to get their side of the story?\n")
    
    print("Who would you like to talk to?\n")
    print("1: Billy and Clara")
    print("2: Flint and Whistle\n")
    b_and_c: list[Agent] = [agent for agent in agents if agent.name in ["Billy \"Snake Eyes\" Thompson", "Miss Clara"]]
    f_and_w: list[Agent] = [agent for agent in agents if agent.name in ["Marshal Flint", "Whistle"]]
    selection = int(input(f"Enter a number (1-2): ")) - 1
    agent_order:list[Agent] = b_and_c if selection == 0 else f_and_w

    #Another time-bound convo
    responses_left = 12
    conversation = Conversation(agent_order+[player], prompts['single_person_conversation_complex'], setting, llm)
    while responses_left > 0:
        #DO THIS BETTER?, this pokes the AI if it speaks first, else we deal with the player and skip to AI
        if responses_left == 6:
            message = '[Enters the room]'
        else:
            message = input(f'{player.name}: ')
        #Normal response conversation and message printing 
        responses: list[ConversationResponse] = conversation.converse(message)
        for i, r in enumerate(responses):
            if r.text: print(f'{r.agent}: {r.text}')
            if r.conversation_ends: responses_left = 0

        responses_left -= 1

    print("\nA sudden gunshot rings out, interrupting your conversation. a distant gunshot rings out, causing panic. The townsfolk scatter, heading to their homes or businesses to seek cover.\n")

def second_day_afternoon(llm, prompts: dict, setting: dict, agents:list[Agent], player:PlayerAgent):
    print("\nThe town is quieter now, and the townspeoples' nerves are on edge. You have the chance to speak to one more person in-depth. \n")
    
    # Select a person to talk to
    print("Who would you like to talk to?")
    for i, agent in enumerate(agents):
        print(f'{str(i+1)}: {agent.name} -- {agent.short_description}')
    selection = int(input(f"Enter a number (1-4): ")) - 1
    print()
    selected_agent = agents[selection]
    print(f'\nTime to talk to {selected_agent.name}\n')

    # Have a simple time-bounded conversation
    agent_order = [player, selected_agent]
    conversation = Conversation(agent_order, prompts['single_person_conversation_complex'], setting, llm)
    responses_left = 6
    while responses_left > 0:
        message = input(f'{player.name}: ')
        responses: list[ConversationResponse] = conversation.converse(message)
        for i, r in enumerate(responses):
            if r.text: print(f'{r.agent}: {r.text}')
            if r.conversation_ends: responses_left = 0

        responses_left -= 1

    print("\nThe conversation has ended.\n")