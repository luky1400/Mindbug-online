# Mindbug Online

This project is a non-commerical digital replica of the [Mindbug](https://boardgamegeek.com/boardgame/345584/mindbug-first-contact) card game.

![image](images/game_images/fav_icon.png)

## Current Features

- 2-player turn-based game loop
- Realtime multiplayer rooms with [FastAPI](https://fastapi.tiangolo.com) + [Socket.IO](https://Socket.IO)
- [React](https://react.dev) browser UI

![image](images/game_images/screen_room.png)

![image](images/game_images/screen_game.png)

![image](images/game_images/screen_use_mindbug.png)

## Play with friend online

### 1) Play the game at [mindbug-online.vercel.app](http://mindbug-online.vercel.app). The backend is deployed on Render and the frontend on Vercel.

### 2) Tunnel your local server with ngrok

1. Create account in [ngrok](https://ngrok.com) (free version is available).
2. Install ngrok

On Mac:

```bash
brew install --cask ngrok
```

Then authenticate once with your account token from ngrok.com:

```bash
ngrok config add-authtoken YOUR_TOKEN
```

3. Run in your project directory

```bash
python3 -m pip install -r requirements.txt
cd frontend
npm install
npm run build
cd ..
python3 -m uvicorn web_app:app --host 0.0.0.0 --port 8000
```

4. In another terminal, use

```bash
ngrok http 8000
```

That starts the turnnel and gives you a public https://... URL.

#### Multiplayer flow

1. Both players open the same URL
2. First player creates a room.
3. Choose the card sets for that room. `First Contact` is always included, and any additional `CardSet` values can be enabled before creating the room.
4. Share the invite code with the second player.
5. Second player enters the code and clicks Join room.
6. Game starts. Both players receive live state updates through Socket.IO.

### Files

- `base_classes.py` - core game engine and state
- `cards.py` - card pool definitions
- `enums.py` - defined enums
- `main.py` - CLI game runner
- `web_app.py` - FastAPI + Socket.IO multiplayer backend
- `web/index.html` - basic frontend UI
- `frontend/` - React + TypeScript multiplayer frontend
- `requirements.txt` - Python dependencies

## Local run (for development)

### Terminal (CLI) version

```bash
python3 main.py
```

### Run tests

```bash
PYTHONPATH=. pytest tests/**/*.py
```

### Multiplayer web version (FastAPI + Socket.IO)

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start server:

```bash
python3 -m uvicorn web_app:app --reload
```

Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### Frontend (React + TypeScript + Bootstrap)

The new frontend source lives in `frontend/`.

Install frontend dependencies:

```bash
cd frontend
npm install
```

Run frontend dev server:

```bash
npm run dev
```

Build frontend for FastAPI production serving:

```bash
npm run build
```

After build, FastAPI serves `frontend/dist/index.html` at `/` automatically.  
If `frontend/dist` does not exist, FastAPI falls back to `web/index.html`.

Open: [http://localhost:5173](http://localhost:5173)
