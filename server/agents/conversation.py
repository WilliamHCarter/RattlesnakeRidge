import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Union

from server.agents.agent import Agent, PlayerAgent

logger = logging.getLogger(__name__)


@dataclass
class ConversationResponse:
    text: str
    agent: str
    conversation_ends: bool


@dataclass
class LLMData:
    client: Any  # OpenAI client
    model: str
    prompt: str
    extra_flavor: dict[str, str]


class Conversation:
    def __init__(self, agents: list[Agent | PlayerAgent], llmd: LLMData):
        # Declare vars
        self.agents = agents
        self.llmd = llmd
        self.agent_llm_data_map = {}

        # Create individual LLMData for each agent with their personalized prompt
        for agent in agents:
            if not isinstance(agent, PlayerAgent):
                individual_prompt = llmd.prompt.format(
                    **{**agent._raw, **llmd.extra_flavor}
                )
                agent_llmd = LLMData(
                    client=llmd.client,
                    model=llmd.model,
                    prompt=individual_prompt,
                    extra_flavor=llmd.extra_flavor,
                )
                self.agent_llm_data_map[agent] = agent_llmd

    def __parse_response(self, agent: Agent, text: str) -> ConversationResponse:
        # Remove thinking tags (e.g., <think>...</think> or <thinking>...</thinking>)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        text = text.strip()

        # Remove the leading "{name}:"
        text = text.lstrip(agent.name + ":")

        # If the text starts with "[QUIT]", the conversation
        # is over and that command should be stripped.
        terminate_prefix = "<quit>"
        if text.startswith(terminate_prefix):
            text = text[len(terminate_prefix) :].lstrip()
            # Remove any </quit> as well
            text = text.rstrip("</quit>")
            return ConversationResponse(text, agent.name, True)
        return ConversationResponse(text, agent.name, False)

    # Cycles the agents to the next one.
    # (We cycle and not iterate so that the conversation order can be easily observed externally by inspecting the Conversation object)
    def cycle_agents(self):
        curr = self.agents.pop(0)
        self.agents.append(curr)

    def begin_conversation(self) -> list[ConversationResponse]:
        """Starts a conversation without player input"""
        return self.converse("[Conversation begins]")

    # Loops through each member of the conversation and allows them to speak.
    def converse(self, message: str) -> list[ConversationResponse]:
        responses: list[ConversationResponse] = []
        carried_message = message

        # If the first agent is a PlayerAgent, skip it.
        if isinstance(self.agents[0], PlayerAgent):
            self.cycle_agents()

        while not isinstance(self.agents[0], PlayerAgent):
            res, mes = self.__talk(self.agents[0], carried_message)
            responses.append(res)

            # Add message to all agents' memory
            for a in self.agents:
                a._memory.save_context({"input": carried_message}, {"text": res.text})

            self.cycle_agents()
            carried_message = res.text

        return responses

    def speak_directly(self, message: str, agent: Agent) -> list[ConversationResponse]:
        if agent not in self.agents:
            raise ValueError(f"Agent {agent.name} is not in the conversation")

        responses: list[ConversationResponse] = []

        # Converse directly with the target agent without disturbing turn order
        res, mes = self.__talk(agent, message)
        responses.append(res)

        # Add message to all agents' memory
        for a in self.agents:
            a._memory.save_context({"input": message}, {"text": res.text})

        return responses

    # Makes a single agent speak given a message.
    def __talk(self, agent: Agent, message: str):
        if isinstance(agent, PlayerAgent):
            raise ValueError("PlayerAgent shouldn't talk via this method")

        # Get the agent's individual LLMData from the mapping
        agent_llmd = self.agent_llm_data_map[agent]

        # Build conversation messages
        messages = []

        # System message is the agent's personalized prompt
        messages.append({"role": "system", "content": agent_llmd.prompt})

        # Add conversation history from memory
        for msg in agent._memory.messages:
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                messages.append({"role": "assistant", "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": message})

        try:
            # Make direct OpenAI API call with agent's individual LLMData
            response = agent_llmd.client.chat.completions.create(
                model=agent_llmd.model,
                messages=messages,
                max_tokens=500,
                temperature=0.05,
                stop=["\n"],
            )

            raw_response = response.choices[0].message.content or ""
            res: ConversationResponse = self.__parse_response(agent, raw_response)

            # Log token usage (basic logging)
            logger.info(
                "invoked llm for agent %s. response_length=%d",
                agent.name,
                len(raw_response),
            )

            # Create a simple message object for memory
            class SimpleMessage:
                def __init__(self, role: str, content: str):
                    self.role = role
                    self.content = content

            msg = SimpleMessage(role=agent.name, content=res.text)
            return res, msg

        except Exception as e:
            logger.error(f"Error calling OpenAI API for agent {agent.name}: {e}")
            # Return a fallback response
            fallback_response = f"{agent.name}: I'm not sure what to say right now."
            res = self.__parse_response(agent, fallback_response)

            class SimpleMessage:
                def __init__(self, role: str, content: str):
                    self.role = role
                    self.content = content

            msg = SimpleMessage(role=agent.name, content=res.text)
            return res, msg
