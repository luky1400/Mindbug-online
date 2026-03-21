from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

import socketio
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from base_classes import Game
from cards import get_card_pool



class CreateGameRequest(BaseModel):
    player_name: str = Field(default="Player 1", min_length=1, max_length=50)


class JoinGameRequest(BaseModel):
    player_name: str = Field(default="Player 2", min_length=1, max_length=50)


class LegacyNewGameRequest(BaseModel):
    player1: str = Field(default="Player 1", min_length=1, max_length=50)
    player2: str = Field(default="Player 2", min_length=1, max_length=50)


class PlayCardRequest(BaseModel):
    hand_index: int = Field(ge=0)


class MindbugResponseRequest(BaseModel):
    use_mindbug: bool = False


class AttackRequest(BaseModel):
    attacker_index: int = Field(ge=0)
    defender_index: int | None = Field(default=None, ge=0)
    hunter_target_override: bool = True


class DefendRequest(BaseModel):
    defender_index: int | None = Field(default=None, ge=0)


@dataclass
class SessionPlayer:
    player_id: str
    name: str
    player_index: int
    connected_sids: set[str] = field(default_factory=set)


class GameSession:
    def __init__(self, game_id: str) -> None:
        self.game_id = game_id
        self.players: list[SessionPlayer] = []
        self.game: Game | None = None
        self.lock = Lock()

    def create_player(self, player_name: str) -> SessionPlayer:
        if len(self.players) >= 2:
            raise ValueError("This room already has two players.")
        player = SessionPlayer(
            player_id=str(uuid4()),
            name=player_name,
            player_index=len(self.players),
        )
        self.players.append(player)
        if len(self.players) == 2:
            self.game = Game(
                [self.players[0].name, self.players[1].name],
                starting_lives=3,
                starting_hand_size=5,
                starting_draw_pile_size=5,
                players_start_with_mindbugs=2,
                await_mindbug_response=True,
                enforce_turn_action_limit=True,
                auto_end_turn_after_successful_play=True,
            )
            self.game.start_game(card_pool=get_card_pool())
        return player

    def get_player(self, player_id: str) -> SessionPlayer:
        for player in self.players:
            if player.player_id == player_id:
                return player
        raise KeyError(player_id)

    def serialize_for(self, player_id: str) -> dict[str, Any]:
        player = self.get_player(player_id)
        opponent = next((item for item in self.players if item.player_id != player_id), None)
        if self.game is None:
            return {
                "game_id": self.game_id,
                "room_status": "WAITING_FOR_PLAYER",
                "game_state": "WAITING_FOR_PLAYER",
                "turn_player": None,
                "winner": None,
                "viewer_player_id": player.player_id,
                "viewer_player_name": player.name,
                "viewer_player_index": player.player_index,
                "opponent_player_name": None if opponent is None else opponent.name,
                "is_viewer_turn": False,
                "viewer": None,
                "opponent": None,
                "log": ["Waiting for second player to join."],
                "pending_mindbug": None,
                "pending_defense": None,
                "pending_frenzy_attacker_index": None,
                "connected_players": len(self.players),
                "max_players": 2,
                "invite_code": self.game_id,
            }

        state = self.game.get_state(viewer_index=player.player_index)
        state.update(
            {
                "game_id": self.game_id,
                "viewer_player_id": player.player_id,
                "connected_players": len(self.players),
                "max_players": 2,
                "invite_code": self.game_id,
            }
        )
        return state


class GameStore:
    def __init__(self) -> None:
        self._sessions: dict[str, GameSession] = {}
        self._lock = Lock()

    def create_game(self, player_name: str) -> tuple[GameSession, SessionPlayer]:
        session = GameSession(game_id=str(uuid4())[:8])
        with self._lock:
            self._sessions[session.game_id] = session
        with session.lock:
            player = session.create_player(player_name)
        return session, player

    def join_game(self, game_id: str, player_name: str) -> tuple[GameSession, SessionPlayer]:
        session = self.get_session(game_id)
        with session.lock:
            player = session.create_player(player_name)
        return session, player

    def get_session(self, game_id: str) -> GameSession:
        with self._lock:
            session = self._sessions.get(game_id)
        if session is None:
            raise KeyError(game_id)
        return session

    def get_session_and_player(self, game_id: str, player_id: str) -> tuple[GameSession, SessionPlayer]:
        session = self.get_session(game_id)
        with session.lock:
            player = session.get_player(player_id)
        return session, player


class LegacyGameStore:
    def __init__(self) -> None:
        self._games: dict[str, Game] = {}
        self._lock = Lock()

    def create_game(self, player1: str, player2: str) -> tuple[str, Game]:
        game = Game(
            [player1, player2],
            starting_lives=3,
            starting_hand_size=5,
            starting_draw_pile_size=5,
            players_start_with_mindbugs=2,
            await_mindbug_response=True,
        )
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


fastapi_app = FastAPI(title="Mindbug Prototype API", version="0.2.0")
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
store = GameStore()
legacy_store = LegacyGameStore()
web_root = Path(__file__).parent / "web"
frontend_dist_root = Path(__file__).parent / "frontend" / "dist"
card_images_root = Path(__file__).parent / "images" / "card_images" / "English"
fastapi_app.mount("/static", StaticFiles(directory=web_root), name="static")
fastapi_app.mount("/card-images", StaticFiles(directory=card_images_root), name="card-images")
if (frontend_dist_root / "assets").exists():
    fastapi_app.mount("/assets", StaticFiles(directory=frontend_dist_root / "assets"), name="frontend-assets")


def _normalize_player_name(raw_name: str, fallback: str) -> str:
    return raw_name.strip() or fallback


def _game_response(session: GameSession, player: SessionPlayer) -> dict[str, Any]:
    return {
        "game_id": session.game_id,
        "player_id": player.player_id,
        "state": session.serialize_for(player.player_id),
    }


def _require_active_game(session: GameSession) -> Game:
    if session.game is None:
        raise ValueError("Waiting for second player to join.")
    return session.game


def _get_legacy_game(game_id: str) -> Game:
    try:
        return legacy_store.get_game(game_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc


def _ensure_turn_owner(game: Game, player_index: int) -> None:
    if game.turn != player_index:
        raise ValueError("It is not your turn.")


def _ensure_pending_mindbug_responder(game: Game, player_index: int) -> None:
    pending = game._pending_mindbug_decision
    if pending is None:
        raise ValueError("There is no pending Mindbug decision.")
    if pending.responding_player_index != player_index:
        raise ValueError("Waiting for the other player to answer the Mindbug prompt.")


def _ensure_pending_defense_responder(game: Game, player_index: int) -> None:
    pending = game._pending_defense_decision
    if pending is None:
        raise ValueError("There is no pending defense decision.")
    if pending.defending_player_index != player_index:
        raise ValueError("Waiting for the defending player to choose a blocker or lose 1 life.")


async def _emit_state_to_player(session: GameSession, player: SessionPlayer) -> None:
    payload = {"state": session.serialize_for(player.player_id)}
    for sid in list(player.connected_sids):
        await sio.emit("state_update", payload, to=sid)


async def _broadcast_session_state(session: GameSession) -> None:
    for player in list(session.players):
        await _emit_state_to_player(session, player)


@fastapi_app.get("/")
def index() -> FileResponse:
    frontend_index = frontend_dist_root / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return FileResponse(web_root / "index.html")


@fastapi_app.post("/game/new")
def new_game(payload: CreateGameRequest) -> dict[str, Any]:
    session, player = store.create_game(_normalize_player_name(payload.player_name, "Player 1"))
    return _game_response(session, player)


@fastapi_app.post("/legacy-game/new")
def legacy_new_game(payload: LegacyNewGameRequest) -> dict[str, Any]:
    game_id, game = legacy_store.create_game(
        _normalize_player_name(payload.player1, "Player 1"),
        _normalize_player_name(payload.player2, "Player 2"),
    )
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/game/{game_id}/join")
def join_game(game_id: str, payload: JoinGameRequest) -> dict[str, Any]:
    try:
        session, player = store.join_game(game_id, _normalize_player_name(payload.player_name, "Player 2"))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game not found.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _game_response(session, player)


@fastapi_app.get("/game/{game_id}/state")
def game_state(game_id: str, player_id: str = Query(..., min_length=1)) -> dict[str, Any]:
    try:
        session, player = store.get_session_and_player(game_id, player_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Game or player not found.") from exc
    return _game_response(session, player)


@fastapi_app.get("/legacy-game/{game_id}/state")
def legacy_game_state(game_id: str) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/legacy-game/{game_id}/play-card")
def legacy_play_card(game_id: str, payload: PlayCardRequest) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    try:
        game.play_card(hand_index=payload.hand_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/legacy-game/{game_id}/mindbug-response")
def legacy_mindbug_response(game_id: str, payload: MindbugResponseRequest) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    try:
        game.respond_to_mindbug(payload.use_mindbug)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/legacy-game/{game_id}/attack")
def legacy_attack(game_id: str, payload: AttackRequest) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    try:
        game.attack(
            attacker_index=payload.attacker_index,
            defender_index=payload.defender_index,
            hunter_target_override=payload.hunter_target_override,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/legacy-game/{game_id}/defend")
def legacy_defend(game_id: str, payload: DefendRequest) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    try:
        game.defend(payload.defender_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"game_id": game_id, "state": game.get_state()}


@fastapi_app.post("/legacy-game/{game_id}/end-turn")
def legacy_end_turn(game_id: str) -> dict[str, Any]:
    game = _get_legacy_game(game_id)
    try:
        game.end_turn()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"game_id": game_id, "state": game.get_state()}


@sio.event
async def connect(sid: str, environ: dict[str, Any], auth: dict[str, str] | None) -> None:
    if not auth:
        raise ConnectionRefusedError("Missing authentication payload.")

    game_id = auth.get("gameId")
    player_id = auth.get("playerId")
    if not game_id or not player_id:
        raise ConnectionRefusedError("Missing game or player identifier.")

    try:
        session, player = store.get_session_and_player(game_id, player_id)
    except KeyError as exc:
        raise ConnectionRefusedError("Game or player not found.") from exc

    with session.lock:
        player.connected_sids.add(sid)
    await sio.save_session(sid, {"game_id": game_id, "player_id": player_id})
    await _broadcast_session_state(session)


@sio.event
async def disconnect(sid: str) -> None:
    session_info = await sio.get_session(sid)
    if not session_info:
        return

    try:
        session, player = store.get_session_and_player(session_info["game_id"], session_info["player_id"])
    except KeyError:
        return

    with session.lock:
        player.connected_sids.discard(sid)
    await _broadcast_session_state(session)


async def _get_socket_context(sid: str) -> tuple[GameSession, SessionPlayer]:
    session_info = await sio.get_session(sid)
    if not session_info:
        raise ValueError("Socket session was not initialized.")
    try:
        return store.get_session_and_player(session_info["game_id"], session_info["player_id"])
    except KeyError as exc:
        raise ValueError("Game or player not found.") from exc


async def _handle_socket_action(sid: str, callback: callable) -> dict[str, Any]:
    try:
        session, player = await _get_socket_context(sid)
        with session.lock:
            callback(session, player)
        await _broadcast_session_state(session)
        return {"ok": True}
    except ValueError as exc:
        await sio.emit("action_error", {"message": str(exc)}, to=sid)
        return {"ok": False, "error": str(exc)}


@sio.event
async def request_state(sid: str) -> dict[str, Any]:
    try:
        session, player = await _get_socket_context(sid)
        await _emit_state_to_player(session, player)
        return {"ok": True}
    except ValueError as exc:
        await sio.emit("action_error", {"message": str(exc)}, to=sid)
        return {"ok": False, "error": str(exc)}


@sio.event
async def play_card(sid: str, payload: dict[str, Any]) -> dict[str, Any]:
    def action(session: GameSession, player: SessionPlayer) -> None:
        game = _require_active_game(session)
        _ensure_turn_owner(game, player.player_index)
        game.play_card(hand_index=int(payload["hand_index"]))

    return await _handle_socket_action(sid, action)


@sio.event
async def attack(sid: str, payload: dict[str, Any]) -> dict[str, Any]:
    def action(session: GameSession, player: SessionPlayer) -> None:
        game = _require_active_game(session)
        _ensure_turn_owner(game, player.player_index)
        defender_index = payload.get("defender_index")
        game.attack(
            attacker_index=int(payload["attacker_index"]),
            defender_index=None if defender_index is None else int(defender_index),
            hunter_target_override=bool(payload.get("hunter_target_override", True)),
        )

    return await _handle_socket_action(sid, action)


@sio.event
async def defend(sid: str, payload: dict[str, Any]) -> dict[str, Any]:
    def action(session: GameSession, player: SessionPlayer) -> None:
        game = _require_active_game(session)
        _ensure_pending_defense_responder(game, player.player_index)
        defender_index = payload.get("defender_index")
        game.defend(None if defender_index is None else int(defender_index))

    return await _handle_socket_action(sid, action)


@sio.event
async def end_turn(sid: str) -> dict[str, Any]:
    def action(session: GameSession, player: SessionPlayer) -> None:
        game = _require_active_game(session)
        _ensure_turn_owner(game, player.player_index)
        game.end_turn()

    return await _handle_socket_action(sid, action)


@sio.event
async def mindbug_response(sid: str, payload: dict[str, Any]) -> dict[str, Any]:
    def action(session: GameSession, player: SessionPlayer) -> None:
        game = _require_active_game(session)
        _ensure_pending_mindbug_responder(game, player.player_index)
        game.respond_to_mindbug(bool(payload.get("use_mindbug", False)))

    return await _handle_socket_action(sid, action)
