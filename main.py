from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI, FakeListChatModel
import os

from agents import Agent, AgentConversation


load_dotenv()
#For local builds, go to .env.template file and follow directions.
api_key = os.environ.get('LLM_API_KEY')

model = 'gpt-3.5-turbo'
# llm = ChatOpenAI(openai_api_key=api_key, model=model)
llm = FakeListChatModel(verbose=True, responses=['Howdy, stranger. What brings you to these parts today?'])

flint_agent = Agent(datafile='data/flint.yaml')
base_prompt = """You are {name}. {long_description}

Here is the visitor now to ask you a question, converse with them given your situation.

Remember, you are simply the {short_name}. You will receive a history of your previous conversations and the current response from the vistor. Once you respond to the visitor, they will respond back to you and so on, so there is no need to speak for them.

Previous conversation:
{{history}}

New visitor response: {{message}}
Response: """
conversation = AgentConversation(flint_agent, base_prompt, llm)

user_message = input("What would you like to say? ")
print(f'> {user_message}')
response = conversation.talk(user_message)
print(f'< {response}')

print(flint_agent._memory.load_memory_variables({}))
