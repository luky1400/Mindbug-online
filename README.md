# Mindbug Python Prototype

This project replicates of a Mindbug-style card game.

- [Czech rules](https://www.rexhry.cz/storage/instructions/mb.rulebook.v3.cze_.web_.pdf), [English rules](https://mindbug.me/wp-content/uploads/2023/08/mindbug-rulebook-ENGLISH-small.pdf)

## Run

### 1) Terminal (CLI) version

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
2. Choose the card sets for that room. `First Contact` is always included, and any additional `CardSet` values can be enabled before creating the room.
3. Share the invite code with the second player.
4. Join that room from a second browser window or another device.
5. Both players receive live state updates through Socket.IO.

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
- Mindbug steal mechanic
- Realtime multiplayer rooms with FastAPI + Socket.IO
- Separate player sessions with hidden opponent hands
- Creature combat with `TOUGH`, `POISONOUS`, `HUNTER`, `FRENZY`, and `SNEAKY` creature types
- Creature actions are supported
- Life tracking and winner detection
- Web API for room creation, join, and session restore
- Room-level card set selection for multiplayer games
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
- **Improve UI layout**
  - make Game UI to fit one screen size - user cannot roll up and down
  - upravit obrazku dle pravidel (+ když najedu with mouse cursor on any of discard_piles, it will render cards in it)
  - dát na rozklikávatko (vpravo nahoře): pravidla, logs, cards in game - rozdělené do tabs podle sets (include also number of copies of each card)
- **UI screens:**
  - seperate create/join room and Game
- **UI additonal:**
  - visualize that TOUGH has 0 tough_charges left (2 options: odlisit, když má 1 nebo 2 nabití?)
  - možnost zvětšit i cards_laid_out (+ in discard pile)
  - Když defender vybira, jestli a cim bude branit, tak mu ukazat kartu utocnika (nejak ji zvyraznit nebo presunout do prostred).
  - Hide redundant information in UI
    - text pod kartami
    - Discard Pile dát nějak nastranu a karty zobrazit, pouze když na to user clickne
  - udělat nejakou signalizaci, kteá upozorní hrace, ze je na tahu (play_card/attack, Mindbug, Defend, etc.)
  - Kliknout a zvetsit celou ruku najednou - udelat to same, jako 2x klik, ale pro vsechny karty najednou. Dát karty v ruce bliz k sobe a zvetsit.
  - add icons to buttons - attack, play_card, End turn (lepší by bylo místo click button, přetahovat, ale to by bylo moc tezke)


## TODO - game rules

- "Pokud probíhá více efektů současně (například pokud se dvě nestvůry porazí navzájem), rozhoduje o pořadí vyhodnocení efektů hráč, jenž je na tahu. Vždy dokončete vyhodnocování jednoho efektu předtím, než začnete vyhodnocovat další."
- Jiný naming:
  - efekty schopnosti: Příchod, ..
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i Češtinu
- udělat funkce pro tyhle termíny: Odložit, Ovládnout nestvůru
- (Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.)


## Nice to have

- add persistent database-backed sessions so rooms survive server restarts.
- add option: Surrender
- add Time limit for action (play_card, attack, use_mindMindbug?, defend?)
- add other sets
- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem.
V případě shody tento proces opakujte."
- make all images the same resolution size
- [QA](https://www.zatrolene-hry.cz/spolecenska-hra/mozkozrout-12630/otazky/)


## Bugs

- 

## Documentation notes

- 2 main action function: play_card, attack
  - resolved plays and attacks automatically trigger end_turn()
- apply_ongoing_effect() - effect is being recalculated - in the beginning of the turn?
- App.tsx: the multiplayer client clears selections immediately when a defense response is sent
- Create room now lets the host choose which sets are used for that room. First Contact is always selected and cannot be unchecked, while the remaining CardSet values can be enabled. The selected sets are sent in the create-room request, stored on the room, used when the game starts, and shown in the UI in both the room metadata and room status area.

