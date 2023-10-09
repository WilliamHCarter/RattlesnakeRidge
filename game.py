from scenes import first_day_intro, first_night_cutscene, second_day_intro, second_day_afternoon, final_confrontation

# A mapping of scene names to scene functions
SCENES = {
    'first_day_intro': first_day_intro,
    'first_night_cutscene': first_night_cutscene,
    'second_day_intro': second_day_intro,
    'second_day_afternoon': second_day_afternoon,
    'final_confrontation': final_confrontation,
}

def play(game_state, user_input):
    # Get the current scene from the game state
    current_scene = game_state.get('current_scene', 'first_day_intro')

    # Get the scene function from the SCENES mapping
    scene_function = SCENES.get(current_scene)

    if scene_function:
        # Call the scene function and pass the current game state and user input
        response, new_game_state = scene_function(game_state, user_input)
        return response, new_game_state

    # Handle the case where the scene is not found
    return "System Error, scene not found", None
