from dataclasses import dataclass
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from langchain.prompts import PromptTemplate
from langchain.schema.messages import ChatMessage
from server.agents.agent import Agent, PlayerAgent


LLM_t = ChatOpenAI | FakeListChatModel


@dataclass
class ConversationResponse:
    text: str
    agent: str
    conversation_ends: bool


@dataclass
class LLMData:
    llm: LLM_t
    prompt: str
    extra_flavor: dict


class Conversation:
    def __init__(self, agents: list[Agent | PlayerAgent], llmd: LLMData):
        # Declare vars
        self.agents = agents
        self.conversations = []
        self.formatted_prompts = []

        # Create the prompts and conversations
        for i, agent in enumerate(agents):
            self.formatted_prompts.append(
                llmd.prompt.format(**{**agent._raw, **llmd.extra_flavor})
            )

            # Initialize the conversations
            if not isinstance(agent, PlayerAgent):
                self.conversations.append(
                    LLMChain(
                        llm=llmd.llm,
                        prompt=PromptTemplate.from_template(self.formatted_prompts[i]),
                        verbose=False,
                        memory=self.agents[i]._memory,
                    )
                )
            else:
                self.conversations.append("player")

    def __parse_response(self, agent: Agent, text: str) -> ConversationResponse:
        # If the text starts with "[QUIT]", the conversation
        # is over and that command should be stripped.
        terminate_prefix = "[QUIT]"
        if text.startswith(terminate_prefix):
            text = text[len(terminate_prefix) :].lstrip()
            return ConversationResponse(text, agent.name, True)
        return ConversationResponse(text, agent.name, False)

    # Cycles the agents and conversations to the next one.
    # (We cycle and not iterate so that the conversation order can be easily observed externally by inspecting the Conversation object)
    def cycle_agents(self):
        curr = self.agents.pop(0)
        self.agents.append(curr)
        tmp = self.conversations.pop(0)
        self.conversations.append(tmp)

    # Loops through each member of the conversation and allows them to speak.
    def converse(self, message: str) -> list[ConversationResponse]:
        responses: list[ConversationResponse] = []
        carried_message = message

        # If the first agent is a PlayerAgent, skip it.
        if isinstance(self.agents[0], PlayerAgent):
            self.cycle_agents()

        while not isinstance(self.agents[0], PlayerAgent):
            res, mes = self.__talk(self.agents[0], self.conversations[0], carried_message)
            responses.append(res)
            
            for a in self.agents:
                a._memory.chat_memory.add_message(mes)

            self.cycle_agents()
            carried_message = res.text

        return responses


    def speak_directly(self, message: str, agent: Agent) -> list[ConversationResponse]:
        if agent not in self.agents:
            raise ValueError(f"Agent {agent.name} is not in the conversation")

        conversation = self.conversations[self.agents.index(agent)]
        responses: list[ConversationResponse] = []

        # Converse directly with the target agent without disturbing turn order
        res, mes = self.__talk(agent, conversation, message)
        responses.append(res)
        for a in self.agents:
            a._memory.chat_memory.add_message(mes)

        return responses

    # Makes a single agent speak given a message.
    def __talk(self, agent: Agent, conversation, message: str):
        if isinstance(agent, PlayerAgent):
            raise ValueError("PlayerAgent shoudn't talk via this method")
        raw_response = conversation({"message": message})
        res: ConversationResponse = self.__parse_response(agent, raw_response["text"])

        # We need to remove and rename the AIMessage that gets added automatically
        # and re-add it as a ChatMessage with the correct label
        cm = agent._memory.chat_memory
        cm.messages = cm.messages[:-1]
        msg: ChatMessage = ChatMessage(role=agent.name, content=res.text)
        # Return the generated response
        return res, msg
