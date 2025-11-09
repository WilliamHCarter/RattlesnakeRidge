from typing import Any
import yaml
from langchain.memory import ConversationBufferMemory

def load_agent_data(filename: str) -> dict[str, Any]:
    with open(filename, 'r') as file:
        raw = file.read()
    raw_agent_data: dict[str, Any] = yaml.safe_load(raw)
    return raw_agent_data


class Agent:
    _raw: dict[str, Any]
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
    _raw: dict[str, Any] = {
        'name': 'You',
        'short_name': 'You',
        'subtitle': '',
        'short_description': '',
        'long_description': '',
        'opinions': '',
        'clues': '',
        'introduction': '',
        'intro_talks_first': False,
    }

    def __init__(self):  # pyright: ignore[reportMissingSuperCall]
        # Don't call super().__init__() since parent requires datafile parameter
        # and PlayerAgent uses class-level _raw instead
        self._memory: ConversationBufferMemory = ConversationBufferMemory()
