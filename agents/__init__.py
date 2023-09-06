from dataclasses import dataclass
import yaml

from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.messages import ChatMessage


def load_agent_data(filename: str) -> dict:
    with open(filename, 'r') as file:
        raw = file.read()
    raw_agent_data = yaml.safe_load(raw)
    return raw_agent_data


class Agent:
    _raw: dict
    _memory: ConversationBufferMemory

    def __init__(self, datafile: str):
        self._memory = ConversationBufferMemory()
        self._raw = load_agent_data(datafile)

    @property
    def name(self) -> str:
        return str(self._raw['name'])

    @property
    def short_description(self) -> str:
        return str(self._raw['subtitle'])

    @property
    def introduction(self) -> str:
        if 'introduction' in self._raw:
            return str(self._raw['introduction'])
        return 'INTRODUCTION'

    @property
    def does_talk_first_on_first_meeting(self) -> bool:
        return self._raw['intro_talks_first']


@dataclass
class ConversationResponse:
    text: str
    conversation_ends: bool


class AgentConversation:
    def __init__(self, agent: Agent, prompt: str, extra_flavor: dict, llm):
        # Join the agent information with the flavor information
        flavor = {**agent._raw, **extra_flavor}
        self.formatted_prompt = prompt.format(**flavor)
        
        self.agent = agent
        self.conversation = LLMChain(
            llm=llm,
            prompt=PromptTemplate.from_template(self.formatted_prompt),
            verbose=False,
            memory=self.agent._memory
        )

    def __parse_response(self, text: str) -> ConversationResponse:
        # If the text starts with "[QUIT]", the conversation
        # is over and that command should be stripped.
        terminate_prefix = '[QUIT]'
        if text.startswith(terminate_prefix):
            text = text[len(terminate_prefix):].lstrip()
            return ConversationResponse(text, True)
        return ConversationResponse(text, False)


    def talk(self, user_message: str) -> ConversationResponse:
        full_response = self.conversation({"message": user_message})
        response = self.__parse_response(full_response['text'])

        # We need to remove and rename the AIMessage that gets added automatically
        # and re-add it as a ChatMessage with the correct label
        cm = self.agent._memory.chat_memory
        cm.messages = cm.messages[:-1]
        desired = ChatMessage(role=self.agent.name, content=response.text)
        cm.add_message(desired)

        # Return the generated response
        return response

