import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Generator

from server import pending_streams
from server.agents.conversation import Agent, Conversation, LLM_t, LLMData, PlayerAgent
from server.commands import *

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GameData:
    llm: LLM_t
    actors: list[Agent]
    player: PlayerAgent
    prompts: dict[str, str]
    setting_data: dict[str, str]


UserInput_t = str | None
SceneReturn_t = Generator[Command, UserInput_t, None]
Scene_t = Callable[[GameData], SceneReturn_t]


def make_conversation(
    game_data: GameData,
    order: list[Agent],
    prompt_name: str = "single_person_conversation_complex",
) -> Conversation:
    llm_data = LLMData(
        game_data.llm, game_data.prompts[prompt_name], game_data.setting_data
    )
    return Conversation(order, llm_data)


def have_conversation(conversation: Conversation, max_player_messages: int):
    """
    Manage a conversation between player and agents.
    Agent responses will stream in real-time.
    """

    logger.info(
        f"*** HAVE_CONVERSATION CALLED *** starting conversation with {len(conversation.agents)} agents"
    )

    # Initial agent greeting (now streaming!)
    logger.info("have_conversation: getting initial agent greetings")
    initial_responses = conversation.begin_conversation()
    logger.info(f"have_conversation: got {len(initial_responses)} initial responses")
    for r in initial_responses:
        logger.debug(f"have_conversation: got initial greeting from {r.agent}: {r.text}")

        # Create a simple streaming response for the initial greeting
        stream_id = str(uuid.uuid4())
        logger.info(f"have_conversation: created initial greeting stream_id: {stream_id}")

        # Create a simple generator that yields the greeting as chunks
        def initial_greeting_generator():
            # Don't include the agent prefix since frontend handles it
            text = r.text
            # Yield the text in small chunks for streaming effect
            words = text.split()
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")

        # Find the actual agent object from the conversation
        actual_agent = None
        for agent in conversation.agents:
            if agent.name == r.agent:
                actual_agent = agent
                break

        # Store the generator
        pending_streams[stream_id] = {
            "generator": initial_greeting_generator(),
            "conversation": conversation,
            "agent": actual_agent or r.agent,  # Store the agent object or fall back to name
            "message": "[Conversation begins]",
        }

        logger.info(f"have_conversation: yielding StreamingMessageCommand for initial greeting from {r.agent}")
        yield StreamingMessageCommand(
            message="",  # Placeholder, real content comes from stream
            stream_id=stream_id,
            agent_name=r.agent,
        )

    # Now handle player turns
    for turn in range(max_player_messages):
        logger.info(
            f"have_conversation: starting turn {turn + 1}/{max_player_messages}"
        )
        # Get player input
        logger.debug("have_conversation: yielding MessageCommand for user input")
        message = yield MessageCommand("Your response:")
        logger.info(f"have_conversation: received user message: '{message}'")
        assert message is not None
        # Cycle to next agent (skip PlayerAgent)
        logger.debug(
            f"have_conversation: current agent order: {[agent.name for agent in conversation.agents]}"
        )
        if isinstance(conversation.agents[0], PlayerAgent):
            logger.debug("have_conversation: cycling past PlayerAgent")
            conversation.cycle_agents()
        # Skip any remaining PlayerAgents
        while isinstance(conversation.agents[0], PlayerAgent):
            logger.debug("have_conversation: skipping additional PlayerAgent")
            conversation.cycle_agents()
        # Check if we still have agents to respond
        if len(conversation.agents) == 0:
            logger.info(
                "have_conversation: no more agents to respond, ending conversation"
            )
            break
        next_agent = conversation.agents[0]
        logger.info(f"have_conversation: next agent to respond: {next_agent.name}")

        # Stream the agent's response
        logger.info("have_conversation: creating streaming response")
        try:
            stream_id = str(uuid.uuid4())
            logger.info(f"have_conversation: created stream_id: {stream_id}")

            logger.debug(
                f"have_conversation: calling converse with message='{message}', stream=True"
            )
            stream_gen = conversation.converse(message, stream=True)

            if stream_gen is not None:
                # Store both the generator and conversation state for memory management
                logger.info(
                    "have_conversation: storing stream generator and conversation state"
                )
                pending_streams[stream_id] = {
                    "generator": stream_gen,
                    "conversation": conversation,
                    "agent": next_agent,
                    "message": message,
                }
                logger.debug(
                    f"have_conversation: pending_streams now has {len(pending_streams)} streams"
                )

                # Yield streaming command - frontend will establish SSE connection
                logger.info(
                    f"have_conversation: yielding StreamingMessageCommand for agent {next_agent.name}"
                )
                yield StreamingMessageCommand(
                    message="",  # Placeholder, real content comes from stream
                    stream_id=stream_id,
                    agent_name=next_agent.name,
                )
            else:
                logger.warning(
                    "have_conversation: converse returned None stream_gen, falling back to non-streaming"
                )
                # Fall back to non-streaming response
                responses = conversation.converse(message, stream=False)
                logger.info(
                    f"have_conversation: got {len(responses)} fallback responses"
                )
                for r in responses:
                    logger.debug(
                        f"have_conversation: yielding fallback response from {r.agent}"
                    )
                    yield MessageDelayCommand(f"{r.agent}: {r.text}")

                # Cycle agents for fallback response
                conversation.cycle_agents()

        except Exception as e:
            logger.error(
                f"have_conversation: streaming failed, falling back to non-streaming: {e}"
            )
            # Fall back to non-streaming response
            try:
                responses = conversation.converse(message, stream=False)
                logger.info(
                    f"have_conversation: got {len(responses)} fallback responses"
                )
                for r in responses:
                    logger.debug(
                        f"have_conversation: yielding fallback response from {r.agent}"
                    )
                    yield MessageDelayCommand(f"{r.agent}: {r.text}")

                # Cycle agents for fallback response
                conversation.cycle_agents()
            except Exception as fallback_error:
                logger.error(
                    f"have_conversation: fallback also failed: {fallback_error}"
                )
                # Try to provide a simple error message
                yield MessageDelayCommand(
                    f"{next_agent.name}: I'm having trouble responding right now. Please try again."
                )
                conversation.cycle_agents()

    logger.info("have_conversation: conversation completed")
