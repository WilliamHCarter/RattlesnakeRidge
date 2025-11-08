# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Rattlesnake Ridge is a multi-agent ML mystery game where a player investigates a murder in a western town by conversing with 4 AI-powered suspects. The game uses LangChain with OpenAI's API to power agent conversations that can provide clues or deceive the player based on their role in the crime.

## Development Commands

### Backend (Python/Flask)

**Local development with fake LLM:**
```bash
python local.py
```
This runs a terminal-based version using a `FakeListChatModel` for testing without API costs.

**Run server with Docker:**
```bash
# Build the Docker image
docker build -t my-server .

# Run with environment variables
docker run -p 5000:5000 --env-file=.env my-server
```
Server runs on http://localhost:5000

**Run tests:**
```bash
pytest server_tests/
```

### Frontend (React/TypeScript/Vite)

Navigate to `client/` directory:
```bash
cd client
npm install
npm run dev      # Development server at http://localhost:5173
npm run build    # TypeScript compilation + Vite build
npm run lint     # ESLint with TypeScript
```

## Architecture

### Backend: Scene-Based Game State Machine

The core game loop is implemented as a **generator-based state machine** where scenes yield Commands to the frontend:

- **Session** (`server/game.py`): Manages game state and scene progression. Maintains a `scene_stack` (defined in `server/scenes/rattlesnake_ridge.py`) and calls `.send()` on the current scene generator with user input
- **Scene**: A generator function that yields `Command` objects (defined in `server/commands.py`). Scenes control conversation flow and story progression
- **Commands** (`server/commands.py`): Type-safe dataclasses that represent game outputs:
  - `MessageCommand`: Display text and wait for user input
  - `MessageDelayCommand`: Display text with a delay, no input required
  - `SelectOptionCommand`: Present multiple choice options
  - `SceneEndCommand`: End the current scene and advance to next
  - `SoundDelayCommand`: Play sound effect with delay

**Scene structure** (`server/scenes/`):
- `core.py`: Defines `Scene_t`, `GameData`, and helper functions like `make_conversation()` and `have_conversation()`
- `rattlesnake_ridge.py`: Contains all 5 game scenes in `SCENE_ORDER` list (first_day, first_night, second_day_morning, second_day_afternoon, final_confrontation)

### Agent System

**Agent** (`server/agents/agent.py`): Represents a character loaded from YAML files in `server/data/characters/`. Contains name, description, memories, and LangChain `ConversationBufferMemory`.

**Conversation** (`server/agents/conversation.py`): Manages multi-agent conversations using LangChain. Agents take turns speaking in order, with the player inserted in the rotation. Key methods:
- `begin_conversation()`: Start without player input
- `converse(message)`: Cycles through non-player agents, each responding via LLMChain
- `speak_directly(message, agent)`: Target a specific agent without changing turn order

### Flask Routes

`server/routes.py` exposes REST endpoints:
- `GET /start`: Initialize new game session, returns `game_id`
- `POST /play/<game_id>`: Send user input, receive next Command
- `POST /load/<game_id>`: Retrieve conversation history
- `POST /end/<game_id>`: Clean up game state
- `GET /test`: Health check

Game sessions are stored in-memory in the `game_states` dict.

### Frontend Architecture

**Command Processing Flow**:
1. `API.ts` communicates with Flask backend
2. Backend returns serialized Command objects (`marshal_command()`)
3. `castCommand()` deserializes JSON to typed command objects
4. `ResponseHandler.tsx` interprets commands and updates UI
5. `Typewriter.tsx` handles character-by-character text animation
6. `InputField.tsx` collects and validates user input

**State Management**: React hooks manage game state, conversation history, and UI modes. `localStorage` persists `game_id` for session recovery.

## Configuration

- **Environment**: Copy `.env.template` to `.env` and set:
  - `LLM_API_KEY`: OpenAI API key
  - `SECRET_KEY`: Flask secret
  - `FLASK_ENV`: development/production
  - `VITE_API_ADDRESS`: Backend URL for frontend

- **Game Data** (`server/data/`):
  - `characters/*.yaml`: Character definitions (flint, billy, clara, whistle)
  - `prompts.yaml`: LLM system prompts
  - `setting.yaml`: World/story context

## Key Implementation Details

- The scene generator pattern allows complex branching narratives while maintaining linear code flow
- Player input validation occurs in `Session.is_input_valid()`, checking against the last command's expected input type
- Agents maintain conversation memory via LangChain's `ConversationBufferMemory`, stored per-agent
- The winning condition is hardcoded: selecting "Whistle" in the final confrontation scene
- Frontend uses Tailwind CSS with dark mode support via CSS classes
