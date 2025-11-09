import logging
import re
from dataclasses import dataclass

from langchain.callbacks import get_openai_callback
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI, FakeListChatModel
from langchain.prompts import PromptTemplate
from langchain.schema.messages import ChatMessage

from server.agents.agent import Agent, PlayerAgent

logger = logging.getLogger(__name__)


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
    extra_flavor: dict[str, str]


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
        # Remove thinking tags (e.g., <think>...</think> or <thinking>...</thinking>)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = text.strip()

        # Remove the leading "{name}:"
        text = text.lstrip(agent.name + ":")

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

    def begin_conversation(self) -> list[ConversationResponse]:
        """Starts a conversation without player input"""
        return self.converse("[Conversation begins]", stream=False)

    # Loops through each member of the conversation and allows them to speak.
    def converse(self, message: str, stream: bool = False):
        """
        Conduct conversation with agents.
        If stream=True, returns generator for the first agent's response.
        If stream=False, returns list of all agent responses.
        """
        import logging
        logger = logging.getLogger(__name__)

        logger.debug(f"converse: called with message='{message}', stream={stream}")
        logger.info(f"*** CONVERSE CALLED - stream={stream} ***")
        logger.debug(f"converse: agents order: {[agent.name for agent in self.agents]}")

        # If the first agent is a PlayerAgent, skip it.
        if isinstance(self.agents[0], PlayerAgent):
            logger.debug("converse: cycling past PlayerAgent")
            self.cycle_agents()

        if stream:
            # For streaming, only get the first agent's response as a generator
            if not isinstance(self.agents[0], PlayerAgent):
                logger.info(f"converse: streaming from agent {self.agents[0].name}")
                stream_gen = self.__talk(
                    self.agents[0], self.conversations[0], message, stream=True
                )
                logger.debug("converse: returning stream generator")
                return stream_gen
            else:
                logger.warning("converse: no non-player agent available for streaming")
                return iter([])  # No agent to stream from
        else:
            # Original behavior: all agents respond
            logger.info("converse: using non-streaming mode for all agents")
            responses: list[ConversationResponse] = []
            carried_message = message

            while not isinstance(self.agents[0], PlayerAgent):
                logger.debug(f"converse: getting response from {self.agents[0].name}")
                res, mes = self.__talk(
                    self.agents[0], self.conversations[0], carried_message
                )
                responses.append(res)

                for a in self.agents:
                    a._memory.chat_memory.add_message(mes)

                self.cycle_agents()
                carried_message = res.text

            logger.info(f"converse: returning {len(responses)} responses")
            return responses

    def speak_directly(self, message: str, agent: Agent, stream: bool = False):
        if agent not in self.agents:
            raise ValueError(f"Agent {agent.name} is not in the conversation")

        conversation = self.conversations[self.agents.index(agent)]

        if stream:
            # Return generator for streaming
            return self.__talk(agent, conversation, message, stream=True)
        else:
            # Original behavior: return list of responses
            responses: list[ConversationResponse] = []
            res, mes = self.__talk(agent, conversation, message)
            responses.append(res)
            for a in self.agents:
                a._memory.chat_memory.add_message(mes)
            return responses

    # Makes a single agent speak given a message.
    def __talk(self, agent: Agent, conversation, message: str, stream: bool = False):
        import logging
        logger = logging.getLogger(__name__)

        if isinstance(agent, PlayerAgent):
            raise ValueError("PlayerAgent shoudn't talk via this method")

        logger.debug(f"__talk: agent={agent.name}, message='{message}', stream={stream}")

        if stream:
            # Streaming mode: return a generator that yields tokens
            def stream_generator():
                logger.info(f"stream_generator: *** STARTING STREAM FOR {agent.name} ***")
                full_text = ""
                token_count = 0

                try:
                    # Get the underlying LLM from the LLMChain
                    llm = conversation.llm

                    # Create the prompt the same way LLMChain would by accessing its memory
                    # Get the conversation history from memory
                    memory_buffer = []
                    if hasattr(agent._memory, 'chat_memory') and hasattr(agent._memory.chat_memory, 'messages'):
                        for msg in agent._memory.chat_memory.messages:
                            if hasattr(msg, 'content'):
                                memory_buffer.append(msg.content)

                    # Build the prompt with memory context
                    memory_context = "\n".join(memory_buffer) if memory_buffer else ""
                    full_prompt = f"{memory_context}\n\nHuman: {message}\n\nAssistant:"

                    logger.debug(f"stream_generator: formatted prompt: '{full_prompt[:200]}...'")

                    # Use the LLM directly for streaming
                    with get_openai_callback() as cb:
                        from langchain.schema import HumanMessage
                        messages = [HumanMessage(content=full_prompt)]

                        logger.debug(f"stream_generator: calling llm.stream with {len(messages)} messages")
                        for chunk in llm.stream(messages):
                            logger.debug(f"stream_generator: got chunk: {chunk}")

                            # Extract text from chunk (we know this works from our testing)
                            if hasattr(chunk, 'content'):
                                token = chunk.content
                            elif isinstance(chunk, dict) and 'text' in chunk:
                                token = chunk['text']
                            elif isinstance(chunk, str):
                                token = chunk
                            else:
                                token = str(chunk)

                            logger.debug(f"stream_generator: extracted token: '{token}'")
                            full_text += token
                            token_count += 1

                            # For the first token, strip the agent prefix if present
                            if token_count == 1 and full_text.startswith(f"{agent.name}:"):
                                # Strip the prefix and yield only the content after the prefix
                                stripped_text = full_text[len(f"{agent.name}:"):].lstrip()
                                if stripped_text:
                                    yield stripped_text
                            else:
                                yield token

                        logger.info(f"stream_generator: finished streaming {token_count} tokens for {agent.name}")
                        logger.debug(f"stream_generator: full text: '{full_text}'")

                        if cb.prompt_tokens != 0 or cb.completion_tokens != 0:
                            logger.info(
                                "invoked llm (streaming). prompt tokens=%d ; completion tokens=%d ; cost=%f",
                                cb.prompt_tokens,
                                cb.completion_tokens,
                                cb.total_cost,
                            )

                except Exception as e:
                    logger.error(f"stream_generator: error during streaming: {e}")
                    raise e

            logger.debug(f"__talk: returning stream generator for {agent.name}")
            return stream_generator()
        else:
            # Non-streaming mode: original behavior
            with get_openai_callback() as cb:
                raw_response = conversation({"message": message})
                res: ConversationResponse = self.__parse_response(
                    agent, raw_response["text"]
                )
                # Avoid logging if both values are zero. This likely means we aren't using an OpenAI model
                # at this time.
                if cb.prompt_tokens != 0 or cb.completion_tokens != 0:
                    logger.info(
                        "invoked llm. prompt tokens=%d ; completion tokens=%d ; cost=%f",
                        cb.prompt_tokens,
                        cb.completion_tokens,
                        cb.total_cost,
                    )

            # We need to remove and rename the AIMessage that gets added automatically
            # and re-add it as a ChatMessage with the correct label
            cm = agent._memory.chat_memory
            cm.messages = cm.messages[:-1]
            msg: ChatMessage = ChatMessage(role=agent.name, content=res.text)
            # Return the generated response
            return res, msg
