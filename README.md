# Mindbug Python Prototype

This project contains a playable terminal prototype of a Mindbug-style card game.

- [Czech rules](https://www.rexhry.cz/storage/instructions/mb.rulebook.v3.cze_.web_.pdf), [English rules](https://mindbug.me/wp-content/uploads/2023/08/mindbug-rulebook-ENGLISH-small.pdf)

## Run

### 1) Terminal version

```bash
python3 main.py
```

### 2) Web version (FastAPI + basic frontend)

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
- Creature combat with `TOUGH`, `POISONOUS`, `HUNTER`, `FRENZY`, and `SNEAKY` creature types
- Creature actions are supported
- Life tracking and winner detection
- Web API for game actions
- Basic browser UI

## Files

- `base_classes.py` - core game engine and state
- `cards.py` - card pool definitions
- `enums.py` - shared enums
- `main.py` - CLI game runner
- `web_app.py` - FastAPI backend and endpoints
- `web/index.html` - basic frontend UI
- `requirements.txt` - Python dependencies

## TODO

- finish backend to work well
  - handle that player or opponent can choose which cards to play or discard
  - add tests regularly for things that are not working
- rewrite functions - attack, play_card, .. e.g. player plays_card and only then opponent decides whether to use mindbug or not.- we must remove mindbug argument from play_card function. - put use mindbug logic inside play_card function
  - so that frontend would wokr as expected (e.g. player plays a card and then defender needs to decide whether to use mindbug or not, ..)
- Add online multiplayer turns using Socket.io (async).
- (Replace in-memory game store with database-backed sessions.)

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

- add other sets
- Add proper authentication
- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem.
V případě shody tento proces opakujte."
- [QA](https://www.zatrolene-hry.cz/spolecenska-hra/mozkozrout-12630/otazky/)

## Bugs

- In UI - user can play_card or attack multiple times per turn

