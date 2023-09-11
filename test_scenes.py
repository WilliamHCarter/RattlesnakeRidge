from copy import copy
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from agents.conversation import Conversation, ConversationResponse
from agents.agent import Agent, PlayerAgent

def test_select_scene(prompts: dict, setting: dict):
    # Dummy name haha
    player_name = 'Jimmy'
    character_names = ['flint', 'billy', 'clara', 'whistle']

    agents = [Agent(datafile=f'data/characters/{name}.yaml') for name in character_names]
    player = PlayerAgent(datafile='data/characters/player.yaml')
    remaining_intro = copy(agents)

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
        print(selected_agent.introduction)
        print()

        # Set the Model
        llm = FakeListChatModel(
            verbose=True, 
            responses=[f"Hi there, I'm {selected_agent.name}", 'That is not nice', '[QUIT] This conversation is over.']
        )
        #llm = ChatOpenAI(openai_api_key=api_key, model=model)


        # Have a simple time-bounded conversation
        agent_order = [selected_agent, player] if selected_agent.does_talk_first_on_first_meeting else [player, selected_agent]
        conversation = Conversation(agent_order, prompts['single_person_conversation_complex'], setting, llm)
        responses_left = 6
        while responses_left > 0:
            #DO THIS BETTER?, this pokes the AI if it speaks first, else we deal with the player and skip to AI
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

def test_multiagent_scene(prompts:dict, setting:dict):
    # Dummy name heehee
    player_name = 'Jammy'
    character_names = ['flint', 'billy', 'clara', 'whistle']
    agents = [Agent(datafile=f'data/characters/{name}.yaml') for name in character_names]
    player = PlayerAgent(datafile='data/characters/player.yaml')
    agent_order = agents + [player]
    
    # Set the Model
    llm = FakeListChatModel(
        verbose=True, 
        responses=[f"Hi there, I'm somebody, check my nametag.", 'That is not nice', ' This conversation is over.']
    )
    #llm = ChatOpenAI(openai_api_key=api_key, model=model)
    print("You are approached by Flint, Billy, and Clara. They want to talk to you.\n")
    
    #Another time-bound convo
    responses_left = 6
    conversation = Conversation(agent_order, prompts['single_person_conversation_complex'], setting, llm)
    while responses_left > 0:
        #DO THIS BETTER?, this pokes the AI if it speaks first, else we deal with the player and skip to AI
        if responses_left == 6:
            message = '[Enters the room]'
        else:
            message = input(f'{player_name}: ')
        #Normal response conversation and message printing 
        responses = conversation.converse(message)
        for i, r in enumerate(responses):
            if r.text: print(f'{r.agent}: {r.text}')
            if r.conversation_ends: responses_left = 0

        responses_left -= 1

    print("\nThe conversation has ended as the sun was setting.\n")