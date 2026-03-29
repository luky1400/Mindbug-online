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

## TODO - backend

- add tests regularly for things that are not working
- Simplify and unify code
- Investigate if logs make sense - is order correct? ... Add log "Player 1" attacks.

## TODO - frontend

- [Inspiration](https://www.google.com/search?q=mindbug+sharkdog+kills+target+before+combat&sca_esv=a02f3e9b87f4a5a7&biw=928&bih=929&sxsrf=ANbL-n7HQ14P5EW6K1BdKcbbh2tpTjZctA%3A1774706171802&ei=-93HabrZML6N-d8Py-v86A0&ved=0ahUKEwj6ws3X38KTAxW-Rv4FHcs1H90Q4dUDCBE&uact=5&oq=mindbug+sharkdog+kills+target+before+combat&gs_lp=Egxnd3Mtd2l6LXNlcnAiK21pbmRidWcgc2hhcmtkb2cga2lsbHMgdGFyZ2V0IGJlZm9yZSBjb21iYXQyBRAhGKABMgUQIRigAUiAX1CkC1iPXnABeACQAQCYAYYBoAGVFaoBBDE5Ljm4AQPIAQD4AQGYAhygArsVwgIIEAAYsAMY7wXCAgsQABiABBiwAxiiBMICCBAAGBYYChgewgIFEAAY7wXCAggQABiABBiiBMICBxAhGKABGAqYAwCIBgGQBgWSBwUxNy4xMaAHk1-yBwUxNi4xMbgHtxXCBwYxLjIzLjTIBzmACAA&sclient=gws-wiz-serp#fpstate=ive&vld=cid:9515da25,vid:kjw0N0Uhvm8,st:0)
- **Improve UI layout**
  - make Game UI to fit one screen size - users cannot roll up and down
  - upravit obrazovku dle pravidel (+ když najedu with mouse cursor on any of discard_piles, it will render cards in it)
    - Discard Pile dát nějak nastranu a karty zobrazit, pouze když na to user klikne - zobrazi se stejne modal window a user muze kliknout na hide.
- **UI additonal:**
  - Když defender vybira, jestli a cim bude branit, tak mu ukazat kartu utocnika - zvyrznit ji:
    - Prompt: can you make orange/red border/glow to card that was selected as attacker. This border should only apply until defender is selected.
  - Show attack/play/end turn buttons only during players turn, otherwise show defend/lose life button.
- dont show Game status: "Your turn". But rather: "Play card or attack" / "Play card" / "Attack."
- Hide redundant information in UI
- udělat nejakou signalizaci (dát Game status mezi Boards), která upozorní hrace, ze je na tahu (play_card/attack, Mindbug, Defend, etc.)
- Refactor hand - dát karty v ruce bliz k sobe a zvetsit. I zvetsit celou ruku najednou? I Smazat Expand button?
- add icons to buttons - attack, play_card, End turn (lepší by bylo místo click button, přetahovat)
- Smazat Close button u Card preview
- Special effects:
  - Hrac ukradnul kartu mozkozroutem
  - when card is defeated
  - drawing cards
  - Hunt/No hunt
  - Hrac utoci
  - Aktivovala se akce
  - Zesnovačka zrušila PLAY akci, ..

## TODO - game rules

- Jiný naming:
  - efekty schopnosti: Příchod, ..
  - Stálé schopnosti (př. Zesnovačka)
  - do své herní oblasti
  - support i pro Češtinu
- udělat funkce pro tyhle termíny: Odložit, Ovládnout nestvůru
- (Síla nestvůry nemůže mít nikdy nižší hodnotu než 1, a to ani v případě, že by některé efekty hodnotu síly upravovaly.)

## Nice to have

- add persistent database-backed sessions so rooms survive server restarts.
- add Time limit for action (play_card, attack, use_mindMindbug?, defend?)
- add other cards from different sets:
  - Spiky shinobi
  - Westside monster
  - Slugapult
  - Sheriff
  - Peach police
  - Puffermech
  - Cave lizard
  - Orange owlmancer
  - Cheery chimpborg
  - Cyber bunny
  - Radisher
  - Earwig assasin
  - Sawn
  - Utility bug
  - Kiwing juicer
  - Radioactive pest
  - Sweet fighter
  - Kitsunsei
  - Catalisk
  - Quetzalcoatl
  - Pesky peas
  - Bullet train
  - Fennel Trickster
  - Blastfish
  - Steelhorn
  - Porcupine teacher
  - Turtle toaster
  - Tiger wasp
  - Spirit maki
  - Gigazaur
  - Space penguin
  - Ghostly underdog
  - Rex Florae
  - Leeklings
  - Coconut crab
  - BATTLEFRUIT KINGDOM
- "Začínajícího hráče určíte tak, že si každý hráč náhodně vylosuje jednu kartu z hromádky nepoužitých karet nestvůr a poté si hráči porovnají sílu těchto karet. Hráč, jehož karta má vyšší hodnotu síly, bude začínajícím hráčem.
V případě shody tento proces opakujte."
- dát na rozklikávatko (vpravo nahoře): pravidla
- [QA](https://www.zatrolene-hry.cz/spolecenska-hra/mozkozrout-12630/otazky/)

## Bugs - backend

- 

## Bugs - frontend

- In Knightmare, Steamforger cards, I dont see green actual strength if it is higher than normal.
- (Opponents cards laid out can be selected for target attack but they have no blue border when selected.)
- I see FRENZY above Hyenix card when deciding whether to play it or not.

## Documentation notes

- 2 main action functions: play_card, attack
  - resolved plays and attacks automatically trigger end_turn()
- apply_ongoing_effect() - effect is being recalculated - in the beginning of the turn?
- App.tsx: the multiplayer client clears selections immediately when a defense response is sent
- Create room now lets the host choose which sets are used for that room. First Contact is always selected and cannot be unchecked, while the remaining CardSet values can be enabled. The selected sets are sent in the create-room request, stored on the room, used when the game starts, and shown in the UI in both the room metadata and room status area.
- TOUGH cards have `TOUGH` badge in the top-right.
- Dynamic badges of special effects only appear when the is actually gained from an effect, not when it is native on the card (e.g. Lone Yeti, Mummy Cat, Snail Thrower effect, Ram Hopper ).
- Rooms are stored only in memory, so if the host server restarts, the game is lost.
- In `_select_cards_for_game()`, after selecting game cards, the remaining cards from the card pool are cloned, shuffled, and stored in `self.unused_pile`
- `Shark_dog():`
  1. HUNTER target resolved early (stored as `hunter_defender`)
  2. ATTACK action fires → sets `_pending_card_action_choice`
  3. Stores `_pending_attack_continuation` with attacker + defender refs → **returns**
  4. Player calls `resolve_pending_card_action()` → choice resolves, Shark Dog defeats a creature
  5. `_continue_attack_after_action_resolution()` runs:
    - If HUNTER target was destroyed → "Combat is cancelled" → `_finalize_attack_action` (handles FRENZY)
    - If HUNTER target survived → `_resolve_combat()` proceeds normally
- Pokud probíhá více efektů současně (například pokud se dvě nestvůry porazí navzájem, nebo jich jenomu hraci umre vice v jednom kole), rozhoduje o pořadí vyhodnocení efektů hráč, jenž je na tahu.

