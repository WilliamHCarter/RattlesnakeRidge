from dataclasses import dataclass
from typing import Generator
from collections.abc import Callable
from server.agents.conversation import Conversation, Agent, LLMData, PlayerAgent
from server.commands import *

@dataclass(frozen=True)
class GameData:
    llm_data: LLMData
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
            prompt_name: str = "single_person_conversation_complex"
        ) -> Conversation:
    llm_data = LLMData(
        client=game_data.llm_data.client,
        model=game_data.llm_data.model,
        prompt=game_data.prompts[prompt_name],
        extra_flavor=game_data.setting_data
    )
    return Conversation(order, llm_data)


def have_conversation(conversation: Conversation, max_player_messages: int):
    responses_left = max_player_messages

    responses = conversation.begin_conversation()

    while responses_left > 0:
        # Display all the responses
        for i, r in enumerate(responses):
            if r.conversation_ends: responses_left = 0
            msg = f"{r.agent}: {r.text}"
            if i < len(responses) - 1 or responses_left == 0:
                yield MessageDelayCommand(msg)
            else:
                # If this is the last response and the player has allowed messages,
                # get input and get new responses
                message = yield MessageCommand(msg)
                responses = conversation.converse(message)

        responses_left -= 1