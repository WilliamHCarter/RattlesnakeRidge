import logging
import uuid

from flask import jsonify, request
from openai import OpenAI

from server import app, logger
from server.session import AI_API_LIMIT, ai_api_usage, game_states
from server.commands import marshal_command
from server.game import Session, initialize_game, play_game
from server.agents.conversation import LLMData

logger = logging.getLogger(__name__)


@app.route("/start", methods=["GET"])
def start_game():
    # Generating a unique game ID
    game_id = str(uuid.uuid4())

    # Create OpenAI client for local Ollama server
    client = OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )

    # Create LLMData for the game
    MODEL = "granite3.1-dense:8b"
    llm_data = LLMData(
        client=client,
        model=MODEL,
        prompt="",  # This will be set per conversation
        extra_flavor={}  # This will be set per conversation
    )

    # Initializing the game state
    game_states[game_id] = initialize_game(llm_data=llm_data)

    logger.info("Created a new game with id %s", game_id)
    return jsonify(game_id=game_id, message="Game started!")


@app.route("/play/<game_id>", methods=["POST"])
def play(game_id):
    user_input = request.json.get("input") if request.json else None
    game_state = game_states.get(game_id)

    if game_state is None:
        logger.warning("`/play` called with an invalid game id %s", game_id)
        return jsonify(error="Invalid game ID"), 400

    if not game_state.is_input_valid(user_input):
        logger.warning(
            'invalid user input provided "%s" for game id %s', user_input, game_id
        )
        return jsonify(error="Bad user input"), 400

    command = play_game(game_state, user_input)

    if user_input != "" and command != "":
        global ai_api_usage
        ai_api_usage += 1
        if ai_api_usage > AI_API_LIMIT:
            logger.error("AI API usage exceeded limit %d", AI_API_LIMIT)
            return jsonify(
                error="Unfortunately we've exceeded our daily limit for AI usage. Please continue your adventure tomorrow."
            ), 429

    return jsonify(response=marshal_command(command))


@app.route("/end/<game_id>", methods=["POST"])
def end_game(game_id):
    if game_id in game_states:
        logger.info("game with id %s ended", game_id)
        del game_states[game_id]
        return jsonify(message="Game data cleared!")
    else:
        logger.info("attempted to end game with id %s, but it does not exist", game_id)
        return jsonify(error="Invalid game ID"), 400


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Success"})


@app.route("/load/<game_id>", methods=["POST"])
def load_game(game_id):
    if game_id not in game_states:
        return jsonify(error="Invalid game ID"), 400
    session: Session = game_states[game_id]
    return jsonify(response=session.logs)


if __name__ == "__main__":
    app.run(debug=True)
