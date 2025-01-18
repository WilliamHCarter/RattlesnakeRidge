import pytest

from server.commands import *

EXAMPLE_MESSAGE = "this is an example message"


def test_ensure_expected_fields():
    message_command = MessageCommand(EXAMPLE_MESSAGE)
    data = marshal_command(message_command)

    # Ensure we have the right fields in the marshalled data
    expected_keys = [
        "is_game_over",
        "expects_user_input",
        "message",
        "do_type_message",
        "character_delay_ms",
        "type",
    ]
    assert all([key in data for key in expected_keys])
    assert len(data) == 2 + 3 + 0 + 1

    # Ensure that the expects_user_input properly overrides the original
    # value.
    assert data["expects_user_input"] == True

    # Ensure message is a required field
    # (it doesn't make sense to send a message without a message)
    with pytest.raises(TypeError):
        MessageCommand()
