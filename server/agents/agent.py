from typing import Any, List, Dict
import yaml

class SimpleConversationMemory:
    """Simple replacement for LangChain's ConversationBufferMemory"""
    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def save_context(self, inputs: Dict[str, str], outputs: Dict[str, str]):
        """Save conversation turn"""
        if 'input' in inputs:
            self.messages.append({'role': 'user', 'content': inputs['input']})
        if 'response' in outputs:
            self.messages.append({'role': 'assistant', 'content': outputs['response']})
        elif 'text' in outputs:
            self.messages.append({'role': 'assistant', 'content': outputs['text']})

    def load_memory_variables(self, inputs: List[str] = None) -> Dict[str, str]:
        """Load conversation history"""
        history = ""
        for msg in self.messages:
            if msg['role'] == 'user':
                history += f"Human: {msg['content']}\n"
            else:
                history += f"Assistant: {msg['content']}\n"
        return {"history": history}

    def clear(self):
        """Clear memory"""
        self.messages.clear()

    @property
    def buffer(self) -> str:
        """Get conversation buffer as string"""
        return self.load_memory_variables()["history"]

def load_agent_data(filename: str) -> dict[str, Any]:
    with open(filename, 'r') as file:
        raw = file.read()
    raw_agent_data: dict[str, Any] = yaml.safe_load(raw)
    return raw_agent_data


class Agent:
    _raw: dict[str, Any]
    _memory: SimpleConversationMemory

    def __init__(self, datafile: str):
        self._memory = SimpleConversationMemory()
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
        self._memory: SimpleConversationMemory = SimpleConversationMemory()
