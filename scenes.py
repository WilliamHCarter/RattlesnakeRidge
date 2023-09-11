from copy import copy
from agents.conversation import Conversation, ConversationResponse
from agents.agent import Agent, PlayerAgent

def first_day_intro(llm, prompts: dict, setting: dict):
    # Dummy name haha
    player_name = 'Jimmy'
    character_names = ['flint', 'billy', 'clara', 'whistle']

    agents = [Agent(datafile=f'data/characters/{name}.yaml') for name in character_names]
    player = PlayerAgent(datafile='data/characters/player.yaml')
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
                message = input(f'{player_name}: ')
            #Normal response conversation and message printing 
            responses = conversation.converse(message)
            for i, r in enumerate(responses):
                if r.text: print(f'{r.agent}: {r.text}')
                if r.conversation_ends: responses_left = 0

            responses_left -= 1

        print("\nThe conversation has ended.\n")

def first_night_cutscene():
    print("The moon is high when a piercing scream echoes through the night. Everyone rushes out to find Whistle's Saloon in disarray – a scuffle has occurred. You notice a bloodied poker card on the floor, the ace of spades. This might be a clue, but to what?")

def second_day_intro(llm, prompts: dict, setting: dict):
    pass