from __future__ import annotations

from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from base_classes import Game
from cards import get_card_pool


### NOTE: To run the web app, use the following command: python3 -m uvicorn web_app:app --reload

class NewGameRequest(BaseModel):
    player1: str = Field(default="Player 1", min_length=1, max_length=50)
    player2: str = Field(default="Player 2", min_length=1, max_length=50)


class PlayCardRequest(BaseModel):
    hand_index: int = Field(ge=0)
    use_opponent_mindbug: bool = False


class AttackRequest(BaseModel):
    attacker_index: int = Field(ge=0)
    defender_index: int | None = Field(default=None, ge=0)
    hunter_target_override: bool = True


class GameStore:
    def __init__(self) -> None:
        self._games: dict[str, Game] = {}
        self._lock = Lock()

    def create_game(self, player1: str, player2: str) -> tuple[str, Game]:
        game = Game([player1, player2], starting_lives=3, starting_hand_size=5, starting_draw_pile_size=5, players_start_with_mindbugs=2)
        game.start_game(card_pool=get_card_pool())
        game_id = str(uuid4())
        with self._lock:
            self._games[game_id] = game
        return game_id, game

    def get_game(self, game_id: str) -> Game:
        with self._lock:
            game = self._games.get(game_id)
        if game is None:
            raise KeyError(game_id)
        return game


app = FastAPI(title="Mindbug Prototype API", version="0.1.0")
store = GameStore()
web_root = Path(__file__).parent / "web"
frontend_dist_root = Path(__file__).parent / "frontend" / "dist"
card_images_root = Path(__file__).parent / "images" / "card_images" / "English"
app.mount("/static", StaticFiles(directory=web_root), name="static")
app.mount("/card-images", StaticFiles(directory=card_images_root), name="card-images")
if (frontend_dist_root / "assets").exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist_root / "assets"), name="frontend-assets")


@app.get("/")
def index() -> FileResponse:
    frontend_index = frontend_dist_root / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return FileResponse(web_root / "index.html")


@app.post("/game/new")
def new_game(payload: NewGameRequest) -> dict:
    game_id, game = store.create_game(payload.player1.strip(), payload.player2.strip())
    return {"game_id": game_id, "state": game.get_state()}


@app.get("/game/{game_id}/state")
def game_state(game_id: str) -> dict:
    try:
        game = store.get_game(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc
    return {"game_id": game_id, "state": game.get_state()}


@app.post("/game/{game_id}/play-card")
def play_card(game_id: str, payload: PlayCardRequest) -> dict:
    try:
        game = store.get_game(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc

    try:
        game.play_card(
            hand_index=payload.hand_index,
            use_opponent_mindbug=payload.use_opponent_mindbug,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"game_id": game_id, "state": game.get_state()}


@app.post("/game/{game_id}/attack")
def attack(game_id: str, payload: AttackRequest) -> dict:
    try:
        game = store.get_game(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc

    try:
        game.attack(
            attacker_index=payload.attacker_index,
            defender_index=payload.defender_index,
            hunter_target_override=payload.hunter_target_override,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"game_id": game_id, "state": game.get_state()}


@app.post("/game/{game_id}/end-turn")
def end_turn(game_id: str) -> dict:
    try:
        game = store.get_game(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc

    try:
        game.end_turn()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"game_id": game_id, "state": game.get_state()}
