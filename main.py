from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI, FakeListChatModel
import os

from agents import Agent, AgentConversation

import yaml
with open('data/prompts.yaml', 'r') as file:
    raw = file.read()
prompts = yaml.safe_load(raw)

load_dotenv()
#For local builds, go to .env.template file and follow directions.
api_key = os.environ.get('LLM_API_KEY')

model = 'gpt-3.5-turbo'
# llm = ChatOpenAI(openai_api_key=api_key, model=model)
llm = FakeListChatModel(verbose=True, responses=['Howdy, stranger. What brings you to these parts today?'])

flint_agent = Agent(datafile='data/flint.yaml')
conversation = AgentConversation(flint_agent, prompts['single_person_conversation'], llm)

# user_message = input("What would you like to say? ")
user_message = "Hello there!"
print(f'> {user_message}')
response = conversation.talk(user_message)
print(f'< {response}')

print(conversation.agent._memory.load_memory_variables({})['history'])
