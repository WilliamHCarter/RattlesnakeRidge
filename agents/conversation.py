from dataclasses import dataclass
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from langchain.prompts import PromptTemplate
from langchain.schema.messages import ChatMessage
from agents.agent import Agent, PlayerAgent


@dataclass
class ConversationResponse:
    text: str
    agent: str
    conversation_ends: bool


@dataclass
class LLMData:
    llm: ChatOpenAI | FakeListChatModel
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

    def __parse_response(self, text: str) -> ConversationResponse:
        # If the text starts with "[QUIT]", the conversation
        # is over and that command should be stripped.
        terminate_prefix = "[QUIT]"
        if text.startswith(terminate_prefix):
            text = text[len(terminate_prefix) :].lstrip()
            return ConversationResponse(text, self.agents[0].name, True)
        return ConversationResponse(text, self.agents[0].name, False)

    # Cycles the agents and conversations to the next one.
    # (We cycle and not iterate so that the conversation order can be easily observed externally by inspecting the Conversation object)
    def cycle_agents(self):
        curr = self.agents.pop(0)
        self.agents.append(curr)
        tmp = self.conversations.pop(0)
        self.conversations.append(tmp)

    # Loops through each member of the conversation and allows them to speak.
    def converse(self, initial_message: str) -> list[ConversationResponse]:
        carried_message = initial_message
        responses: list[ConversationResponse] = []

        # Early check and cycle of player agent, since their message is pre-loaded as initial.
        if isinstance(self.agents[0], PlayerAgent):
            self.cycle_agents()

        while self.agents:
            # If we've looped back to the player, we return. Cycling will be handled on re-entry.
            if isinstance(self.agents[0], PlayerAgent):
                return responses

            # Let the current agent talk
            res, mes = self.__talk(carried_message)
            responses.append(res)
            for a in self.agents:
                a._memory.chat_memory.add_message(mes)

            self.cycle_agents()
            carried_message = res.text

    def speak_directly(self, initial_message: str, agent) -> list[ConversationResponse]:
        # Initialize the response list and carried message
        carried_message = initial_message
        responses: list[ConversationResponse] = []

        # Store the original first agent for later restoration
        original_first_agent = self.agents[0]

        # Cycle through agents until the target agent is at the top
        while self.agents[0] != agent:
            self.cycle_agents()

        # Converse with the target agent
        res, mes = self.__talk(carried_message)
        responses.append(res)
        for a in self.agents:
            a._memory.chat_memory.add_message(mes)

        # Cycle through agents until the original first agent is restored to the top
        while self.agents[0] != original_first_agent:
            self.cycle_agents()

        return responses

    # Makes a single agent speak given a message.
    def __talk(
        self, input_message: str, conv_idx: int = 0
    ) -> tuple[ConversationResponse, ChatMessage]:
        if isinstance(self.conversations[conv_idx], PlayerAgent):
            raise ValueError("PlayerAgent shoudn't talk via this method")
        full_response = self.conversations[conv_idx]({"message": input_message})
        response: ConversationResponse = self.__parse_response(full_response["text"])

        # We need to remove and rename the AIMessage that gets added automatically
        # and re-add it as a ChatMessage with the correct label
        cm = self.agents[conv_idx]._memory.chat_memory
        cm.messages = cm.messages[: conv_idx - 1]
        message = ChatMessage(role=self.agents[conv_idx].name, content=response.text)
        # Return the generated response
        return response, message
