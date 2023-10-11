import yaml
from langchain.memory import ConversationBufferMemory

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
        raise ValueError('No introduction')

    @property
    def does_talk_first_on_first_meeting(self) -> bool:
        return self._raw['intro_talks_first']
    
class PlayerAgent(Agent):
    pass