import { useEffect, useMemo, useRef, useState } from "react";
import type { Socket } from "socket.io-client";
import { createGameSocket, gameApi, socketActions } from "./api/client";
import { BoardZone } from "./components/BoardZone";
import { CardPreviewModal } from "./components/CardPreviewModal";
import { GameLog } from "./components/GameLog";
import { GameOverModal } from "./components/GameOverModal";
import { HandPanel } from "./components/HandPanel";
import type { MultiplayerState } from "./types/game";
import { cardHasTag } from "./utils/cards";

type StoredSession = {
  gameId: string;
  playerId: string;
};

const SESSION_STORAGE_KEY = "mindbug-multiplayer-session";

export function App() {
  const socketRef = useRef<Socket | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [playerId, setPlayerId] = useState<string | null>(null);
  const [state, setState] = useState<MultiplayerState | null>(null);
  const [hostName, setHostName] = useState("Player 1");
  const [joinName, setJoinName] = useState("Player 2");
  const [joinCode, setJoinCode] = useState(() => new URLSearchParams(window.location.search).get("game") || "");

  const [selectedHandIndex, setSelectedHandIndex] = useState<number | null>(null);
  const [selectedAttackerIndex, setSelectedAttackerIndex] = useState<number | null>(null);
  const [selectedDefenderIndex, setSelectedDefenderIndex] = useState<number | null>(null);
  const [statusText, setStatusText] = useState("");
  const [errorText, setErrorText] = useState("");
  const [showGameOver, setShowGameOver] = useState(false);
  const [previewCardLabel, setPreviewCardLabel] = useState<string | null>(null);

  const viewer = state?.viewer || null;
  const opponent = state?.opponent || null;
  const hand = viewer?.hand || [];
  const isWaitingForOpponent = state?.room_status === "WAITING_FOR_PLAYER";
  const gameOver = state?.game_state === "GAME_OVER";
  const canAnswerMindbug = Boolean(state?.pending_mindbug?.response_required_from_viewer);
  const canAnswerDefense = Boolean(state?.pending_defense?.response_required_from_viewer);
  const canAct = Boolean(
    state &&
    viewer &&
    opponent &&
    state.is_viewer_turn &&
    !gameOver &&
    !state.pending_mindbug &&
    !state.pending_defense
  );
  const hasPendingFrenzyAttack = state?.pending_frenzy_attacker_index !== null && state?.pending_frenzy_attacker_index !== undefined;

  const metaText = useMemo(() => {
    if (!state || !gameId) return "Create or join a multiplayer room.";
    if (isWaitingForOpponent) {
      return `Room ${gameId} | Invite code: ${state.invite_code} | Players: ${state.connected_players}/${state.max_players}`;
    }
    return `Room ${gameId} | You: ${state.viewer_player_name} | Turn: ${state.turn_player ?? "-"} | State: ${state.game_state}${state.winner ? ` | Winner: ${state.winner}` : ""}`;
  }, [gameId, isWaitingForOpponent, state]);

  const selectionText = `Hand: ${selectedHandIndex ?? "-"} | Attacker: ${selectedAttackerIndex ?? "-"} | Target/Blocker: ${selectedDefenderIndex ?? "-"}`;

  function persistSession(nextSession: StoredSession) {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(nextSession));
    const url = new URL(window.location.href);
    url.searchParams.set("game", nextSession.gameId);
    window.history.replaceState({}, "", url);
  }

  function clearPersistedSession() {
    localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  function clearSelections() {
    setSelectedHandIndex(null);
    setSelectedAttackerIndex(null);
    setSelectedDefenderIndex(null);
  }

  function getDefenderSelectionPool(sourceState: MultiplayerState | null) {
    if (!sourceState) return [];
    return sourceState.pending_defense?.response_required_from_viewer
      ? sourceState.viewer?.battlefield || []
      : sourceState.opponent?.battlefield || [];
  }

  function normalizeSelections(nextState: MultiplayerState) {
    const previousHand = state?.viewer?.hand || [];
    const previousBoard = state?.viewer?.battlefield || [];
    const previousDefenderPool = getDefenderSelectionPool(state);
    const nextHand = nextState.viewer?.hand || [];
    const nextBoard = nextState.viewer?.battlefield || [];
    const defenderSelectionPool = getDefenderSelectionPool(nextState);

    if (
      selectedHandIndex !== null &&
      (
        selectedHandIndex < 0 ||
        selectedHandIndex >= nextHand.length ||
        previousHand[selectedHandIndex] !== nextHand[selectedHandIndex]
      )
    ) {
      setSelectedHandIndex(null);
    }
    if (
      selectedAttackerIndex !== null &&
      (
        selectedAttackerIndex < 0 ||
        selectedAttackerIndex >= nextBoard.length ||
        previousBoard[selectedAttackerIndex] !== nextBoard[selectedAttackerIndex]
      )
    ) {
      setSelectedAttackerIndex(null);
    }
    if (
      selectedDefenderIndex !== null &&
      (
        selectedDefenderIndex < 0 ||
        selectedDefenderIndex >= defenderSelectionPool.length ||
        previousDefenderPool[selectedDefenderIndex] !== defenderSelectionPool[selectedDefenderIndex]
      )
    ) {
      setSelectedDefenderIndex(null);
    }
    if (
      nextState.pending_frenzy_attacker_index !== null &&
      nextState.pending_frenzy_attacker_index !== undefined
    ) {
      setSelectedAttackerIndex(nextState.pending_frenzy_attacker_index);
    }
  }

  function applyState(nextState: MultiplayerState) {
    const turnChanged = state?.turn_player !== nextState.turn_player;
    const defenseStepEnded = Boolean(state?.pending_defense) && !nextState.pending_defense;
    const mindbugStepEnded = Boolean(state?.pending_mindbug) && !nextState.pending_mindbug;

    if (turnChanged) {
      clearSelections();
    } else if (defenseStepEnded || mindbugStepEnded) {
      setSelectedDefenderIndex(null);
    }

    normalizeSelections(nextState);
    setState(nextState);
    if (nextState.game_state === "GAME_OVER") {
      setShowGameOver(true);
    }
  }

  function connectSocket(nextGameId: string, nextPlayerId: string) {
    socketRef.current?.disconnect();
    const socket = createGameSocket(nextGameId, nextPlayerId, {
      onState: (nextState) => {
        setErrorText("");
        applyState(nextState);
      },
      onError: (message) => {
        setErrorText(message);
      }
    });
    socketRef.current = socket;
  }

  function activateSession(nextGameId: string, nextPlayerId: string, nextState: MultiplayerState) {
    setGameId(nextGameId);
    setPlayerId(nextPlayerId);
    setJoinCode(nextGameId);
    clearSelections();
    setShowGameOver(false);
    applyState(nextState);
    persistSession({ gameId: nextGameId, playerId: nextPlayerId });
    connectSocket(nextGameId, nextPlayerId);
  }

  async function restoreSession(storedSession: StoredSession) {
    try {
      const response = await gameApi.getState(storedSession.gameId, storedSession.playerId);
      activateSession(response.game_id, response.player_id, response.state);
      setStatusText("Reconnected to saved multiplayer session.");
    } catch {
      clearPersistedSession();
    }
  }

  useEffect(() => {
    const rawSession = localStorage.getItem(SESSION_STORAGE_KEY);
    if (!rawSession) return;

    try {
      void restoreSession(JSON.parse(rawSession) as StoredSession);
    } catch {
      clearPersistedSession();
    }
  }, []);

  useEffect(() => {
    return () => {
      socketRef.current?.disconnect();
    };
  }, []);

  async function createGame() {
    setErrorText("");
    try {
      const response = await gameApi.createGame({
        player_name: hostName.trim() || "Player 1"
      });
      activateSession(response.game_id, response.player_id, response.state);
      setStatusText(`Room created. Share invite code ${response.game_id} with the second player.`);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function joinGame() {
    if (!joinCode.trim()) {
      setErrorText("Enter an invite code first.");
      return;
    }
    setErrorText("");
    try {
      const response = await gameApi.joinGame(joinCode.trim(), {
        player_name: joinName.trim() || "Player 2"
      });
      activateSession(response.game_id, response.player_id, response.state);
      setStatusText(`Joined room ${response.game_id}.`);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function refreshState() {
    if (!gameId || !playerId) {
      setErrorText("Create or join a room first.");
      return;
    }
    setErrorText("");
    try {
      const response = await gameApi.getState(gameId, playerId);
      applyState(response.state);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function emitAction(action: () => Promise<{ ok: boolean; error?: string }>, successText: string) {
    setErrorText("");
    try {
      const response = await action();
      if (!response.ok) {
        setErrorText(response.error || "Action failed.");
        return;
      }
      setStatusText(successText);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function playSelectedCard(forcedHandIndex: number | null = null) {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!canAct) return setErrorText("You cannot play a card right now.");
    const handIndex = forcedHandIndex ?? selectedHandIndex;
    if (handIndex === null) return setErrorText("Select a hand card first.");
    await emitAction(() => socketActions.playCard(socketRef.current as Socket, handIndex), "Card played.");
  }

  async function attackSelected() {
    if (!socketRef.current || !state || !viewer) return setErrorText("Create or join a room first.");
    if (!canAct) return setErrorText("You cannot attack right now.");

    const attackerIndex = selectedAttackerIndex;
    if (attackerIndex === null) return setErrorText("Select an attacker first.");

    const attackerLabel = viewer.battlefield[attackerIndex];
    const isHunter = cardHasTag(attackerLabel, "HUNTER");
    const normalizedDefenderIndex =
      selectedDefenderIndex !== null &&
      selectedDefenderIndex >= 0 &&
      selectedDefenderIndex < (opponent?.battlefield.length || 0)
        ? selectedDefenderIndex
        : null;

    if (selectedDefenderIndex !== normalizedDefenderIndex) {
      setSelectedDefenderIndex(normalizedDefenderIndex);
    }

    if (hasPendingFrenzyAttack && attackerIndex !== state.pending_frenzy_attacker_index) {
      return setErrorText("Use the same FRENZY attacker for the second attack, or end turn.");
    }
    if (!isHunter && normalizedDefenderIndex !== null) {
      return setErrorText("Cannot target attack with a non-HUNTER attacker. Remove target and attack again.");
    }

    await emitAction(
      () =>
        socketActions.attack(socketRef.current as Socket, {
          attacker_index: attackerIndex,
          defender_index: isHunter ? normalizedDefenderIndex : null,
          hunter_target_override: true
        }),
      isHunter && normalizedDefenderIndex !== null ? "Hunter attack resolved." : "Attack declared."
    );
  }

  async function defendWithSelectedBlocker() {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!canAnswerDefense) return setErrorText("No defense response is waiting for you.");
    if (selectedDefenderIndex === null) return setErrorText("Select your blocking creature first.");
    if (!state?.pending_defense?.eligible_defender_indices.includes(selectedDefenderIndex)) {
      return setErrorText("Selected creature cannot block this attack.");
    }

    clearSelections();
    await emitAction(
      () => socketActions.defend(socketRef.current as Socket, { defender_index: selectedDefenderIndex }),
      "Blocker selected."
    );
  }

  async function takeLifeLoss() {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!canAnswerDefense) return setErrorText("No defense response is waiting for you.");
    clearSelections();
    await emitAction(
      () => socketActions.defend(socketRef.current as Socket, { defender_index: null }),
      "Attack goes through."
    );
  }

  async function endTurn() {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!state?.is_viewer_turn) return setErrorText("It is not your turn.");
    await emitAction(() => socketActions.endTurn(socketRef.current as Socket), "Turn ended.");
  }

  async function answerMindbug(useMindbug: boolean) {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!canAnswerMindbug) return setErrorText("No Mindbug response is waiting for you.");
    await emitAction(
      () => socketActions.mindbugResponse(socketRef.current as Socket, useMindbug),
      useMindbug ? "Mindbug used." : "Mindbug declined."
    );
  }

  function leaveSession() {
    socketRef.current?.disconnect();
    socketRef.current = null;
    clearPersistedSession();
    setGameId(null);
    setPlayerId(null);
    setState(null);
    clearSelections();
    setStatusText("Session cleared on this device.");
    const url = new URL(window.location.href);
    url.searchParams.delete("game");
    window.history.replaceState({}, "", url);
  }

  function toggleSelected(type: "hand" | "attacker" | "defender", index: number) {
    if (type === "hand") setSelectedHandIndex((current) => (current === index ? null : index));
    if (type === "attacker") setSelectedAttackerIndex((current) => (current === index ? null : index));
    if (type === "defender") setSelectedDefenderIndex((current) => (current === index ? null : index));
  }

  return (
    <main className="app-shell container-xl py-3">
      <section className="card border-0 bg-panel">
        <div className="card-body">
          <div className="d-flex flex-wrap align-items-end gap-3 mb-3">
            <h1 className="app-title m-0 me-auto">Mindbug Multiplayer</h1>
            <button className="btn btn-outline-light" onClick={refreshState} type="button">
              Refresh state
            </button>
            <button className="btn btn-outline-danger" onClick={leaveSession} type="button">
              Leave local session
            </button>
          </div>

          <div className="setup-grid">
            <div className="setup-panel">
              <h2 className="section-title">Create room</h2>
              <label className="text-light w-100">
                Your name
                <input
                  className="form-control mt-1"
                  value={hostName}
                  onChange={(event) => setHostName(event.target.value)}
                />
              </label>
              <button className="btn btn-primary mt-2" onClick={createGame} type="button">
                Create room
              </button>
            </div>

            <div className="setup-panel">
              <h2 className="section-title">Join room</h2>
              <label className="text-light w-100">
                Invite code
                <input
                  className="form-control mt-1"
                  value={joinCode}
                  onChange={(event) => setJoinCode(event.target.value)}
                />
              </label>
              <label className="text-light w-100 mt-2">
                Your name
                <input
                  className="form-control mt-1"
                  value={joinName}
                  onChange={(event) => setJoinName(event.target.value)}
                />
              </label>
              <button className="btn btn-success mt-2" onClick={joinGame} type="button">
                Join room
              </button>
            </div>
          </div>

          <div className="meta-text mt-3">{metaText}</div>
          {statusText ? <div className="status-text">{statusText}</div> : null}
          {errorText ? <div className="error-text">{errorText}</div> : null}
        </div>
      </section>

      {state && viewer ? (
        <div className="row g-3">
          <div className="col-12">
            <section className="card border-0 bg-panel">
              <div className="card-body">
                <div className="d-flex flex-wrap gap-2 align-items-center justify-content-between">
                  <div>
                    <div className="section-title mb-1">Room status</div>
                    <div className="turn-banner">
                      {isWaitingForOpponent
                        ? `Waiting for second player. Share code ${state.invite_code}.`
                        : state.pending_mindbug
                          ? state.pending_mindbug.response_required_from_viewer
                            ? `Respond to ${state.pending_mindbug.acting_player_name}'s ${state.pending_mindbug.card_label}.`
                            : `Waiting for ${state.pending_mindbug.responding_player_name} to answer the Mindbug prompt.`
                          : state.pending_defense
                            ? state.pending_defense.response_required_from_viewer
                              ? `Defend against ${state.pending_defense.attacking_player_name}'s ${state.pending_defense.attacker_label}.`
                              : `Waiting for ${state.pending_defense.defending_player_name} to choose a blocker or lose 1 life.`
                          : state.is_viewer_turn
                            ? "Your turn."
                            : `Waiting for ${state.turn_player}.`}
                    </div>
                  </div>
                  {state.pending_mindbug?.response_required_from_viewer ? (
                    <div className="d-flex gap-2">
                      <button className="btn btn-warning" onClick={() => void answerMindbug(true)} type="button">
                        Use Mindbug
                      </button>
                      <button className="btn btn-outline-light" onClick={() => void answerMindbug(false)} type="button">
                        Decline
                      </button>
                    </div>
                  ) : state.pending_defense?.response_required_from_viewer ? (
                    <div className="d-flex gap-2">
                      <button className="btn btn-outline-light" onClick={() => void defendWithSelectedBlocker()} type="button">
                        Block with selected creature
                      </button>
                      <button className="btn btn-warning" onClick={() => void takeLifeLoss()} type="button">
                        Lose 1 life
                      </button>
                    </div>
                  ) : null}
                </div>
              </div>
            </section>
          </div>

          {!isWaitingForOpponent ? (
            <div className="col-12">
              <section className="card border-0 bg-panel">
                <div className="card-body">
                  <div className="row g-3 align-items-end">
                    <div className="col-md-4">
                      <h2 className="section-title">Play</h2>
                      <button className="btn btn-primary w-100" disabled={!canAct} onClick={() => void playSelectedCard()} type="button">
                        Play selected hand card
                      </button>
                    </div>
                    <div className="col-md-4">
                      <h2 className="section-title">Attack</h2>
                      <button className="btn btn-outline-light w-100" disabled={!canAct} onClick={() => void attackSelected()} type="button">
                        Attack
                      </button>
                      <p className="section-help mt-2 mb-0">
                        Select an enemy target only when your attacker has `HUNTER`. Otherwise click `Attack` without a target and the defender will respond.
                      </p>
                    </div>
                    <div className="col-md-4">
                      <h2 className="section-title">Turn</h2>
                      <button className="btn btn-success w-100 mb-2" disabled={!state.is_viewer_turn || Boolean(gameOver) || canAnswerMindbug || canAnswerDefense} onClick={() => void endTurn()} type="button">
                        End turn
                      </button>
                      <div className="selection-box">{selectionText}</div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          ) : null}

          <div className="col-12">
            <BoardZone
              title={opponent?.name || state.opponent_player_name || "Opponent"}
              player={opponent || { player_index: 1, name: state.opponent_player_name || "Opponent", lives: 0, mindbugs_remaining: 0, hand_count: 0, draw_count: 0, discard_count: 0, battlefield: [], discard: [], hand: [] }}
              battlefieldMode={canAnswerDefense ? "readonly" : "defender"}
              selectedBattlefieldIndex={canAnswerDefense ? null : selectedDefenderIndex}
              onSelectBattlefield={canAnswerDefense ? undefined : (index) => toggleSelected("defender", index)}
            />
          </div>
          <div className="col-12">
            <BoardZone
              title={`${viewer.name}${state.is_viewer_turn ? " (your turn)" : ""}`}
              player={viewer}
              active={state.is_viewer_turn}
              battlefieldMode={canAnswerDefense ? "defender" : "attacker"}
              selectedBattlefieldIndex={canAnswerDefense ? selectedDefenderIndex : selectedAttackerIndex}
              onSelectBattlefield={(index) => toggleSelected(canAnswerDefense ? "defender" : "attacker", index)}
            />
          </div>
          <div className="col-12">
            <section className="card border-0 bg-panel">
              <div className="card-body">
                <HandPanel
                  cards={hand}
                  selectedIndex={selectedHandIndex}
                  onSelect={(index) => toggleSelected("hand", index)}
                  onPreview={(label) => setPreviewCardLabel(label)}
                />
              </div>
            </section>
          </div>
        </div>
      ) : (
        <section className="card border-0 bg-panel">
          <div className="card-body">
            <div className="placeholder">Create a room or join with an invite code to start multiplayer.</div>
          </div>
        </section>
      )}

      <GameLog logLines={state?.log || []} />

      <CardPreviewModal label={previewCardLabel} onClose={() => setPreviewCardLabel(null)} />
      <GameOverModal
        visible={showGameOver && Boolean(gameOver)}
        winner={state?.winner || ""}
        onNewGame={createGame}
        onClose={() => setShowGameOver(false)}
      />
    </main>
  );
}
