import yaml
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


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
        response = self.conversation({"message": user_message})
        return response['text'] 

