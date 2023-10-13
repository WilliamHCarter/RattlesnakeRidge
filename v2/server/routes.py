import uuid
from flask import Flask, request, jsonify
from server.game import play_game, initialize_game  
from server import game_states, app
from server.response import marshal_response

@app.route('/start', methods=['GET'])
def start_game():
    # Generating a unique game ID
    game_id = str(uuid.uuid4())
    
    # Initializing the game state
    game_states[game_id] = initialize_game()

    return jsonify(game_id=game_id, message="Game started!")

@app.route('/play/<game_id>', methods=['POST'])
def play(game_id):
    user_input = request.json.get('input')
    game_state = game_states.get(game_id)
    
    if game_state is None:
        return jsonify(error="Invalid game ID"), 400

    if not game_state.is_input_valid(user_input):
        print(f"Got bad input: {user_input}")
        return jsonify(error="Bad user input"), 400
    
    response = play_game(game_state, user_input)
    return jsonify(response=marshal_response(response))

@app.route('/end/<game_id>', methods=['POST'])
def end_game(game_id):
    if game_id in game_states:
        del game_states[game_id]
        return jsonify(message="Game data cleared!")
    else:
        return jsonify(error="Invalid game ID"), 400

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Success"})


if __name__ == '__main__':
    app.run(debug=True)
