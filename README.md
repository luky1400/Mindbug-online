# Mindbug Python Prototype

This project contains a playable terminal prototype of a Mindbug-style card game.

- [Czech rules](https://www.rexhry.cz/storage/instructions/mb.rulebook.v3.cze_.web_.pdf), [English rules](https://mindbug.me/wp-content/uploads/2023/08/mindbug-rulebook-ENGLISH-small.pdf)

## Run

### 1) Terminal version

```bash
python3 main.py
```

### 2) Multiplayer web version (FastAPI + Socket.IO)

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start server:

```bash
python3 -m uvicorn web_app:app --reload
```

Open:

- [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 3) New scalable frontend (React + TypeScript + Bootstrap)

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

### 4) Multiplayer flow

1. Open the frontend and create a room.
2. Share the invite code with the second player.
3. Join that room from a second browser window or another device.
4. Both players receive live state updates through Socket.IO.

## Run Tests

```bash
PYTHONPATH=. pytest tests/**/*.py
```

Run one file, e.g.:

```bash
PYTHONPATH=. pytest tests/tests_mindbug_use.py
```

## Current Features

- 2-player turn-based game loop
- Play a creature or attack each turn
- Mindbug steal mechanic (1 use per player)
- Realtime multiplayer rooms with FastAPI + Socket.IO
- Separate player sessions with hidden opponent hands
- Creature combat with `TOUGH`, `POISONOUS`, `HUNTER`, `FRENZY`, and `SNEAKY` creature types
- Creature actions are supported
- Life tracking and winner detection
- Web API for room creation, join, and session restore
- React browser UI

## Files

- `base_classes.py` - core game engine and state
- `cards.py` - card pool definitions
- `enums.py` - shared enums
- `main.py` - CLI game runner
- `web_app.py` - FastAPI + Socket.IO multiplayer backend
- `web/index.html` - basic frontend UI
- `frontend/` - React + TypeScript multiplayer frontend
- `requirements.txt` - Python dependencies

## TODO

- finish backend to work well
  - handle that player or opponent can choose which cards to play or discard
  - add tests regularly for things that are not working
  - investigate bug: random cards appear in discard pile
- Improve UI layout
  - dát na rozklikávatko: pravidla, logs
- UI screens:
  - room
- UI additonal:
  - Hide redundant information in UI
    - End turn (if not attacking FRENZY still lives)
  - visualize that TOUGH has 0 tough_charges left
  - možnost zvětšit i cards_laid_out (a in discard pile)
  - Když defender vybira, jestli a cim bude branit, tak mu ukazat kartu utocnika (nejak ji zvyraznit nebo presunout do prostred).

## TODO - game rules

- (Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.)
- Jiný naming:
  - efekty její schopnosti Příchod
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i Češtinu
- udělat funkce pro tyhle termíny: Odložit, Ovládnout nestvůru
- "Současně probíhající efekty:
Pokud probíhá více efektů současně (například pokud se
dvě nestvůry porazí navzájem), rozhoduje o pořadí vyhodnocení efektů hráč, jenž je na tahu. Vždy dokončete
vyhodnocování jednoho efektu předtím, než začnete vyhodnocovat další."

## Nice to have

- add persistent database-backed sessions so rooms survive server restarts.
- add other sets
- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem.
V případě shody tento proces opakujte."
- [QA](https://www.zatrolene-hry.cz/spolecenska-hra/mozkozrout-12630/otazky/)

## Bugs

- 

## Documentation notes

- resolved plays and attacks automatically trigger end_turn()
- App.tsx: the multiplayer client clears selections immediately when a defense response is sent

