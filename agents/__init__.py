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


class AgentConversation:
    def __init__(self, agent: Agent, prompt: str, llm):
        self.agent = agent
        prompt = prompt.format(**agent._raw)

        self.conversation = LLMChain(
            llm=llm,
            prompt=PromptTemplate.from_template(prompt),
            verbose=False,
            memory=self.agent._memory
        )

    def talk(self, user_message: str) -> str:
        full_response = self.conversation({"message": user_message})
        response = full_response['text']

        # We need to remove and rename the AIMessage that gets added automatically
        # and re-add it as a ChatMessage with the correct label
        cm = self.agent._memory.chat_memory
        cm.messages = cm.messages[:-1]
        desired = ChatMessage(role=self.agent.name, content=response)
        cm.add_message(desired)

        # Return the generated response
        return response

