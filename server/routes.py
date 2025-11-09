import json
import logging
import uuid

from flask import Response, jsonify, request, stream_with_context
from langchain.chat_models.openai import ChatOpenAI

from server import (
    AI_API_LIMIT,
    ai_api_usage,
    app,
    game_states,
    logger,
    pending_streams,
)
from server.commands import marshal_command
from server.game import Session, initialize_game, play_game

logger = logging.getLogger(__name__)


@app.route("/start", methods=["GET"])
def start_game():
    # Generating a unique game ID
    game_id = str(uuid.uuid4())

    # Create the llm to use for this game
    # todo:: get the user's provided API key ;)

    # llm = FakeListChatModel(
    #     verbose=True,
    #     responses=[
    #         "Hi there, I'm talking to you.",
    #         "This is a response",
    #         "I say something else too!",
    #         "Ok, goodbye now!",
    #     ],
    # )

    # Use a local Ollama server
    MODEL = "granite3.1-dense:8b"
    llm = ChatOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        model=MODEL,
        streaming=True,  # Enable streaming support
        model_kwargs={"stop": ["\n"]},
    )

    # Initializing the game state
    game_states[game_id] = initialize_game(llm=llm)

    logger.info("Created a new game with id %s", game_id)
    return jsonify(game_id=game_id, message="Game started!")


@app.route("/play/<game_id>", methods=["POST"])
def play(game_id):
    logger.info(f"*** ROUTES.PLAY CALLED *** game_id={game_id}")
    user_input = request.json.get("input") if request.json else None
    game_state = game_states.get(game_id)
    logger.info(f"*** ROUTES.PLAY: user_input='{user_input}', game_state_found={game_state is not None} ***")

    if game_state is None:
        logger.warning("`/play` called with an invalid game id %s", game_id)
        return jsonify(error="Invalid game ID"), 400

    if not game_state.is_input_valid(user_input):
        logger.warning(
            'invalid user input provided "%s" for game id %s', user_input, game_id
        )
        return jsonify(error="Bad user input"), 400

    logger.info(f"*** ROUTES.PLAY: CALLING PLAY_GAME ***")
    command = play_game(game_state, user_input)
    logger.info(f"*** ROUTES.PLAY: GOT COMMAND: {type(command).__name__} ***")

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


@app.route("/stream/<game_id>/<stream_id>", methods=["GET"])
def stream_response(game_id, stream_id):
    """Server-Sent Events endpoint for streaming LLM responses in real-time"""
    logger.info(
        f"stream_response: SSE connection requested for game_id={game_id}, stream_id={stream_id}"
    )
    logger.debug(f"stream_response: pending_streams has {len(pending_streams)} streams")

    if game_id not in game_states:
        logger.warning(f"stream_response: invalid game_id {game_id}")
        return jsonify(error="Invalid game ID"), 400

    if stream_id not in pending_streams:
        logger.warning(f"stream_response: invalid stream_id {stream_id}")
        logger.debug(
            f"stream_response: available stream_ids: {list(pending_streams.keys())}"
        )
        return jsonify(error="Invalid stream ID"), 400

    stream_data = pending_streams[stream_id]
    stream_generator = stream_data["generator"]
    logger.info(f"stream_response: starting SSE stream for {stream_id}")

    def generate():
        try:
            full_text = ""
            token_count = 0
            logger.debug(f"generate: starting token generation for {stream_id}")

            for chunk in stream_generator:
                full_text += chunk
                token_count += 1
                logger.debug(f"generate: yielding token #{token_count}: '{chunk}'")
                # Send each token as SSE data
                yield f"data: {json.dumps({'token': chunk, 'type': 'token'})}\n\n"

            logger.info(
                f"generate: completed streaming {token_count} tokens for {stream_id}"
            )
            logger.debug(f"generate: full text: '{full_text}'")

            # Handle memory management and agent cycling after streaming completes
            stream_data = pending_streams[stream_id]
            conversation = stream_data["conversation"]
            agent = stream_data["agent"]
            message = stream_data["message"]

            # Parse the final response
            from server.agents.conversation import ChatMessage, ConversationResponse

            res: ConversationResponse = conversation._Conversation__parse_response(
                agent, full_text
            )
            msg: ChatMessage = ChatMessage(role=agent.name, content=res.text)

            # Add the final message to all agents' memory
            for a in conversation.agents:
                a._memory.chat_memory.add_message(msg)

            # Cycle to the next agent after streaming completes
            conversation.cycle_agents()
            logger.debug(
                f"generate: cycled agents, new order: {[agent.name for agent in conversation.agents]}"
            )

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'full_text': full_text})}\n\n"

            # Clean up
            logger.debug(f"generate: cleaning up stream {stream_id}")
            del pending_streams[stream_id]
            logger.debug(
                f"generate: pending_streams now has {len(pending_streams)} streams"
            )

        except Exception as e:
            logger.error(
                f"generate: error during streaming for {stream_id}: {e}", exc_info=True
            )
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            if stream_id in pending_streams:
                logger.debug(f"generate: cleaning up stream {stream_id} after error")
                del pending_streams[stream_id]

    logger.info(f"stream_response: creating SSE response for {stream_id}")
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
