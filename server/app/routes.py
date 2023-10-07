from flask import render_template, request, jsonify, session
from app import app
import uuid

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-game', methods=['POST'])
def start_game():
    session['game_id'] = str(uuid.uuid4())  # Generate a unique game ID
    session['game_state'] = 'initial state'  # Initialize the game state
    return jsonify(gameId=session['game_id'], gameState=session['game_state'])

@app.route('/play', methods=['POST'])
def play():
    # Todo: interface with game logic
    pass