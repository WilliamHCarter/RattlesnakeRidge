from server import app

def test_play_with_no_game_returns_400():
    global game_state
    game_state = {}

    with app.test_client() as client:
        response = client.post('/play/nonexistantgameid', json={
            'input': 'dummy input'
        })

        assert response.status_code == 400
