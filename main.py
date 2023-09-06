from copy import copy
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI, FakeListChatModel
import os
import yaml

from agents import Agent, AgentConversation

def load_dict(filename: str) -> dict:
    with open(filename, 'r') as file:
        raw = file.read()
    return yaml.safe_load(raw)

#===== Setup the env and chat model =====#
prompts = load_dict('data/prompts.yaml')
setting = load_dict('data/setting.yaml')
load_dotenv()

#For local builds, go to .env.template file and follow directions.
api_key = os.environ.get('LLM_API_KEY')
model = 'gpt-3.5-turbo'

# Dummy name haha
player_name = 'Jimmy'

character_names = ['flint', 'billy', 'clara', 'whistle']

agents = [Agent(datafile=f'data/characters/{name}.yaml') for name in character_names]
remaining_intro = copy(agents)

for _ in range(4):

    # Select a person to talk to
    if len(remaining_intro) > 1:
        print("Who would you like to talk to?")
        for i, agent in enumerate(remaining_intro):
            print(f'{str(i+1)}: {agent.name} -- {agent.short_description}')
        selection = int(input(f"Enter a number (1-{len(agents)}): ")) - 1
        print()
        selected_agent = remaining_intro[selection]
    else:
        selected_agent = remaining_intro[0]
        print(f'\nTime to talk to {selected_agent.name}\n')

    remaining_intro.remove(selected_agent)

    # Print the introduction for this character
    print(selected_agent.introduction)
    print()

    # Make the conversation
    llm = FakeListChatModel(
        verbose=True, 
        responses=[f"Hi there, I'm {selected_agent.name}", 'That is not nice', '[QUIT] This conversation is over.']
    )
    #llm = ChatOpenAI(openai_api_key=api_key, model=model)
    conversation = AgentConversation(selected_agent, prompts['single_person_conversation'], setting, llm)

    # If the character talks first, prompt them
    if selected_agent.does_talk_first_on_first_meeting:
        response = conversation.talk('[Enters the room]')
        if response.text:
            print(f'{selected_agent.name}: {response.text}')

    # Have a time-bounded conversation
    responses_left = 6
    while responses_left > 0:
        player_message = input(f'{player_name}: ')

        response = conversation.talk(player_message)
        if response.text: print(f'{selected_agent.name}: {response.text}')
        if response.conversation_ends: responses_left = 0

        responses_left -= 1

    print("\nThe conversation has ended.")
