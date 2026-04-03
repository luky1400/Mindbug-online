import { useCallback, useEffect, useRef, useState } from "react";
import type { Socket } from "socket.io-client";
import { createGameSocket, gameApi, socketActions } from "./api/client";
import { BoardZone } from "./components/BoardZone";
import { CardPreviewModal } from "./components/CardPreviewModal";
import { CardBrowserModal } from "./components/CardBrowserModal";
import { GameLog } from "./components/GameLog";
import { HandPanel } from "./components/HandPanel";
import { DefeatedOrderingModal } from "./components/DefeatedOrderingModal";
import { PendingCardActionModal } from "./components/PendingCardActionModal";
import { PendingMindbugModal } from "./components/PendingMindbugModal";
import { CARD_SET_OPTIONS, REQUIRED_CARD_SET, type CardSet, type MultiplayerState } from "./types/game";
import { cardHasTag, parseCardLabel } from "./utils/cards";

type StoredSession = {
  gameId: string;
  playerId: string;
};

const SESSION_STORAGE_KEY = "mindbug-multiplayer-session";

export function App() {
  const socketRef = useRef<Socket | null>(null);
  const prevStateRef = useRef<MultiplayerState | null>(null);
  const [gameId, setGameId] = useState<string | null>(null);
  const [state, setState] = useState<MultiplayerState | null>(null);
  const [hostName, setHostName] = useState("Player 1");
  const [joinName, setJoinName] = useState("Player 2");
  const [joinCode, setJoinCode] = useState(() => new URLSearchParams(window.location.search).get("game") || "");
  const [createRoomSets, setCreateRoomSets] = useState<CardSet[]>([REQUIRED_CARD_SET]);

  const [selectedHandIndex, setSelectedHandIndex] = useState<number | null>(null);
  const [selectedAttackerIndex, setSelectedAttackerIndex] = useState<number | null>(null);
  const [selectedDefenderIndex, setSelectedDefenderIndex] = useState<number | null>(null);
  const [selectedChoiceIndices, setSelectedChoiceIndices] = useState<number[]>([]);
  const selectedChoiceIndicesRef = useRef<number[]>([]);
  const [defeatedOrderingIndices, setDefeatedOrderingIndices] = useState<number[]>([]);
  const [isMindbugModalHidden, setIsMindbugModalHidden] = useState(false);
  const [isChoiceModalHidden, setIsChoiceModalHidden] = useState(false);
  const [isDefeatedOrderingModalHidden, setIsDefeatedOrderingModalHidden] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [errorText, setErrorText] = useState("");
  const [previewCardLabel, setPreviewCardLabel] = useState<string | null>(null);
  const [showLog, setShowLog] = useState(false);
  const [showSurrenderConfirm, setShowSurrenderConfirm] = useState(false);
  const [showLeaveConfirm, setShowLeaveConfirm] = useState(false);
  const [showCardBrowser, setShowCardBrowser] = useState(false);

  type AnimatedCards = {
    viewerHand: Set<number>;
    viewerDiscard: Set<number>;
    opponentDiscard: Set<number>;
    viewerBattlefieldStolen: Set<number>;
    opponentBattlefieldStolen: Set<number>;
  };
  const EMPTY_SET = new Set<number>();
  const emptyAnimatedRef = useRef<AnimatedCards>({
    viewerHand: EMPTY_SET, viewerDiscard: EMPTY_SET, opponentDiscard: EMPTY_SET,
    viewerBattlefieldStolen: EMPTY_SET, opponentBattlefieldStolen: EMPTY_SET,
  });
  const [animatedCards, setAnimatedCards] = useState<AnimatedCards>(emptyAnimatedRef.current);
  const animTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const detectNewCards = useCallback((prevArr: string[], nextArr: string[]): Set<number> => {
    const prevCounts = new Map<string, number>();
    for (const label of prevArr) {
      prevCounts.set(label, (prevCounts.get(label) || 0) + 1);
    }
    const result = new Set<number>();
    for (let i = 0; i < nextArr.length; i++) {
      const remaining = prevCounts.get(nextArr[i]) || 0;
      if (remaining > 0) {
        prevCounts.set(nextArr[i], remaining - 1);
      } else {
        result.add(i);
      }
    }
    return result;
  }, []);

  const viewer = state?.viewer || null;
  const opponent = state?.opponent || null;
  const hand = viewer?.hand || [];
  const inSession = Boolean(gameId && state);
  const isWaitingForOpponent = state?.room_status === "WAITING_FOR_PLAYER";
  const gameOver = state?.game_state === "GAME_OVER";
  const screen = !inSession ? "lobby" : gameOver ? "gameover" : "game";
  const canAnswerMindbug = Boolean(state?.pending_mindbug?.response_required_from_viewer);
  const canAnswerDefense = Boolean(state?.pending_defense?.response_required_from_viewer);
  const canAnswerCardAction = Boolean(state?.pending_card_action?.response_required_from_viewer);
  const canAnswerDefeatedOrdering = Boolean(state?.pending_defeated_ordering?.response_required_from_viewer);
  const hasBlockingMindbugModal = canAnswerMindbug && !isMindbugModalHidden;
  const hasBlockingChoiceModal = canAnswerCardAction && !isChoiceModalHidden;
  const hasBlockingDefeatedOrderingModal = canAnswerDefeatedOrdering && !isDefeatedOrderingModalHidden;
  const canAct = Boolean(
    state &&
    viewer &&
    opponent &&
    state.is_viewer_turn &&
    !gameOver &&
    !state.pending_mindbug &&
    !state.pending_defense &&
    !state.pending_card_action &&
    !state.pending_defeated_ordering
  );
  const hasPendingFrenzyAttack = state?.pending_frenzy_attacker_index !== null && state?.pending_frenzy_attacker_index !== undefined;
  const canManuallyEndTurn = Boolean(
    state &&
    state.is_viewer_turn &&
    !gameOver &&
    !canAnswerMindbug &&
    !canAnswerDefense &&
    !state.pending_card_action &&
    hasPendingFrenzyAttack
  );

  const selectionText = `Hand: ${selectedHandIndex ?? "-"} | Attacker: ${selectedAttackerIndex ?? "-"} | Target/Blocker: ${selectedDefenderIndex ?? "-"}`;
  const pendingCardActionIdentity = state?.pending_card_action
    ? `${state.pending_card_action.action_key}|${state.pending_card_action.source_card_label}|${state.pending_card_action.staged_card_label || ""}|${state.pending_card_action.selection_zone}|${state.pending_card_action.selection_owner_name}|${state.pending_card_action.responding_player_name}`
    : null;
  const pendingMindbugIdentity = state?.pending_mindbug
    ? `${state.pending_mindbug.acting_player_name}|${state.pending_mindbug.card_label}|${state.pending_mindbug.responding_player_name}`
    : null;
  const pendingDefeatedOrderingIdentity = state?.pending_defeated_ordering
    ? state.pending_defeated_ordering.entries.map(e => e.card_label).join("|")
    : null;
  const pendingCardActionName = state?.pending_card_action
    ? parseCardLabel(state.pending_card_action.source_card_label).name
    : "";

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
    selectedChoiceIndicesRef.current = [];
    setSelectedChoiceIndices([]);
  }

  function toggleCreateRoomSet(cardSet: CardSet) {
    if (cardSet === REQUIRED_CARD_SET) return;
    setCreateRoomSets((current) =>
      current.includes(cardSet)
        ? current.filter((value) => value !== cardSet)
        : [...current, cardSet]
    );
  }

  function getDefenderSelectionPool(sourceState: MultiplayerState | null) {
    if (!sourceState) return [];
    return sourceState.pending_defense?.response_required_from_viewer
      ? sourceState.viewer?.battlefield || []
      : sourceState.opponent?.battlefield || [];
  }

  function getPendingCardActionPool(sourceState: MultiplayerState | null) {
    const pending = sourceState?.pending_card_action;
    if (!pending) return [];
    if (pending.selection_zone === "options") return pending.option_labels || [];
    const owner = pending.selection_owner === "viewer" ? sourceState?.viewer : sourceState?.opponent;
    if (!owner) return [];
    if (pending.selection_zone === "hand") return owner.hand || [];
    if (pending.selection_zone === "discard") return owner.discard || [];
    return owner.battlefield || [];
  }

  function normalizeSelections(nextState: MultiplayerState) {
    const prev = prevStateRef.current;
    const previousHand = prev?.viewer?.hand || [];
    const previousBoard = prev?.viewer?.battlefield || [];
    const previousDefenderPool = getDefenderSelectionPool(prev);
    const previousChoicePool = getPendingCardActionPool(prev);
    const nextHand = nextState.viewer?.hand || [];
    const nextBoard = nextState.viewer?.battlefield || [];
    const defenderSelectionPool = getDefenderSelectionPool(nextState);
    const choiceSelectionPool = getPendingCardActionPool(nextState);

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
    const normalizedChoiceIndices = selectedChoiceIndices.filter(
      (index) =>
        index >= 0 &&
        index < choiceSelectionPool.length &&
        previousChoicePool[index] === choiceSelectionPool[index]
    );
    if (normalizedChoiceIndices.length !== selectedChoiceIndices.length) {
      selectedChoiceIndicesRef.current = normalizedChoiceIndices;
      setSelectedChoiceIndices(normalizedChoiceIndices);
    }
    if (
      nextState.pending_frenzy_attacker_index !== null &&
      nextState.pending_frenzy_attacker_index !== undefined
    ) {
      setSelectedAttackerIndex(nextState.pending_frenzy_attacker_index);
    }
  }

  function applyState(nextState: MultiplayerState) {
    const prev = prevStateRef.current;
    const turnChanged = prev?.turn_player !== nextState.turn_player;
    const defenseStepEnded = Boolean(prev?.pending_defense) && !nextState.pending_defense;
    const mindbugStepEnded = Boolean(prev?.pending_mindbug) && !nextState.pending_mindbug;
    const cardActionStepEnded = Boolean(prev?.pending_card_action) && !nextState.pending_card_action;
    const defeatedOrderingStepEnded = Boolean(prev?.pending_defeated_ordering) && !nextState.pending_defeated_ordering;

    if (turnChanged) {
      clearSelections();
    } else if (defenseStepEnded || mindbugStepEnded || cardActionStepEnded || defeatedOrderingStepEnded) {
      setSelectedDefenderIndex(null);
      setSelectedChoiceIndices([]);
    }

    // Detect card animations only when there is a previous game state
    if (prev?.viewer && nextState.viewer) {
      const prevHand = prev.viewer.hand || [];
      const nextHand = nextState.viewer.hand || [];
      const prevViewerDiscard = prev.viewer.discard;
      const nextViewerDiscard = nextState.viewer.discard || [];
      const prevOpponentDiscard = prev.opponent?.discard || [];
      const nextOpponentDiscard = nextState.opponent?.discard || [];

      const newHandIndices = detectNewCards(prevHand, nextHand);
      const newViewerDiscard = detectNewCards(prevViewerDiscard, nextViewerDiscard);
      const newOpponentDiscard = detectNewCards(prevOpponentDiscard, nextOpponentDiscard);

      // Detect Mindbug steal: responding player's battlefield gained a card after mindbug ended
      let viewerBattlefieldStolen = EMPTY_SET;
      let opponentBattlefieldStolen = EMPTY_SET;
      if (mindbugStepEnded && prev.pending_mindbug) {
        const prevViewerBf = prev.viewer.battlefield;
        const nextViewerBf = nextState.viewer?.battlefield || [];
        const prevOpponentBf = prev.opponent?.battlefield || [];
        const nextOpponentBf = nextState.opponent?.battlefield || [];

        if (prev.pending_mindbug.response_required_from_viewer) {
          // Viewer was the responding player — if viewer's battlefield grew, viewer stole it
          const newOnViewer = detectNewCards(prevViewerBf, nextViewerBf);
          if (newOnViewer.size > 0) viewerBattlefieldStolen = newOnViewer;
        } else {
          // Opponent was the responding player — if opponent's battlefield grew, opponent stole it
          const newOnOpponent = detectNewCards(prevOpponentBf, nextOpponentBf);
          if (newOnOpponent.size > 0) opponentBattlefieldStolen = newOnOpponent;
        }
      }

      const hasAny =
        newHandIndices.size > 0 || newViewerDiscard.size > 0 || newOpponentDiscard.size > 0 ||
        viewerBattlefieldStolen.size > 0 || opponentBattlefieldStolen.size > 0;

      if (hasAny) {
        if (animTimerRef.current) clearTimeout(animTimerRef.current);
        setAnimatedCards({
          viewerHand: newHandIndices,
          viewerDiscard: newViewerDiscard,
          opponentDiscard: newOpponentDiscard,
          viewerBattlefieldStolen,
          opponentBattlefieldStolen,
        });
        animTimerRef.current = setTimeout(() => {
          setAnimatedCards(emptyAnimatedRef.current);
          animTimerRef.current = null;
        }, 700);
      }
    }

    normalizeSelections(nextState);
    prevStateRef.current = nextState;
    setState(nextState);
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
    setJoinCode(nextGameId);
    clearSelections();
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

  useEffect(() => {
    setIsChoiceModalHidden(false);
  }, [pendingCardActionIdentity]);

  useEffect(() => {
    setIsMindbugModalHidden(false);
  }, [pendingMindbugIdentity]);

  useEffect(() => {
    setDefeatedOrderingIndices([]);
    setIsDefeatedOrderingModalHidden(false);
  }, [pendingDefeatedOrderingIdentity]);

  async function createGame() {
    setErrorText("");
    try {
      const response = await gameApi.createGame({
        player_name: hostName.trim() || "Player 1",
        selected_sets: createRoomSets
      });
      activateSession(response.game_id, response.player_id, response.state);
      setStatusText(`Room created. Share invite code ${response.game_id} with the second player.`);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  function hideChoiceModal() {
    setIsChoiceModalHidden(true);
  }

  function reopenChoiceModal() {
    setIsChoiceModalHidden(false);
  }

  function hideMindbugModal() {
    setIsMindbugModalHidden(true);
  }

  function reopenMindbugModal() {
    setIsMindbugModalHidden(false);
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
          defender_index: isHunter ? normalizedDefenderIndex : null
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

  async function resolveCardActionChoice(selectedIndicesOverride?: number[]) {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!state?.pending_card_action) return setErrorText("No card action choice is waiting.");
    if (!canAnswerCardAction) return setErrorText("Waiting for the other player to resolve this card action.");
    const pending = state.pending_card_action;
    const selectedIndices = selectedIndicesOverride ?? selectedChoiceIndicesRef.current;
    if (
      selectedIndices.length < pending.min_choices ||
      selectedIndices.length > pending.max_choices
    ) {
      const message =
        pending.min_choices === pending.max_choices
          ? `Select exactly ${pending.min_choices} card${pending.min_choices === 1 ? "" : "s"}.`
          : `Select between ${pending.min_choices} and ${pending.max_choices} cards.`;
      return setErrorText(message);
    }
    await emitAction(
      () =>
        socketActions.resolveCardActionChoice(socketRef.current as Socket, {
          selected_indices: selectedIndices
        }),
      "Card action resolved."
    );
  }

  async function confirmSurrender() {
    setShowSurrenderConfirm(false);
    await emitAction(
      () => socketActions.surrender(socketRef.current as Socket),
      "You surrendered."
    );
  }

  function selectDefeatedOrder(index: number) {
    setDefeatedOrderingIndices(current => {
      if (current.includes(index)) return current;
      return [...current, index];
    });
  }

  function resetDefeatedOrder() {
    setDefeatedOrderingIndices([]);
  }

  async function confirmDefeatedOrdering() {
    if (!socketRef.current) return setErrorText("Create or join a room first.");
    if (!canAnswerDefeatedOrdering) return setErrorText("No DEFEATED ordering is waiting for you.");
    const entries = state!.pending_defeated_ordering!.entries;
    if (defeatedOrderingIndices.length !== entries.length) {
      return setErrorText("Select all DEFEATED cards in order.");
    }
    await emitAction(
      () => socketActions.resolveDefeatedOrdering(socketRef.current as Socket, defeatedOrderingIndices),
      "DEFEATED order chosen."
    );
  }

  function leaveSession() {
    socketRef.current?.disconnect();
    socketRef.current = null;
    clearPersistedSession();
    setGameId(null);
    setState(null);
    clearSelections();
    setStatusText("");
    setErrorText("");
    const url = new URL(window.location.href);
    url.searchParams.delete("game");
    window.history.replaceState({}, "", url);
  }

  function toggleSelected(type: "hand" | "attacker" | "defender", index: number) {
    if (type === "hand") setSelectedHandIndex((current) => (current === index ? null : index));
    if (type === "attacker") setSelectedAttackerIndex((current) => (current === index ? null : index));
    if (type === "defender") setSelectedDefenderIndex((current) => (current === index ? null : index));
  }

  function toggleChoiceIndex(index: number) {
    const pending = state?.pending_card_action;
    if (!pending) return;
    setSelectedChoiceIndices((current) => {
      let next = current;
      if (pending.max_choices === 1) {
        next = current[0] === index ? [] : [index];
      } else if (current.includes(index)) {
        next = current.filter((value) => value !== index);
      } else if (current.length >= pending.max_choices) {
        next = current;
      } else {
        next = [...current, index];
      }
      selectedChoiceIndicesRef.current = next;
      return next;
    });
  }

  const pendingCardActionPool = getPendingCardActionPool(state);

  // ── Lobby screen ──────────────────────────────────────────────────────────
  if (screen === "lobby") {
    return (
      <main className="app-shell container-xl py-3">
        <section className="card border-0 bg-panel">
          <div className="card-body">
            <h1 className="app-title mb-4">Mindbug Multiplayer</h1>

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
                <div className="mt-3">
                  <div className="section-title mb-2">Card sets</div>
                  <div className="set-options">
                    {CARD_SET_OPTIONS.map((cardSet) => {
                      const isRequired = cardSet === REQUIRED_CARD_SET;
                      return (
                        <label className="set-option" key={cardSet}>
                          <input
                            checked={createRoomSets.includes(cardSet)}
                            disabled={isRequired}
                            onChange={() => toggleCreateRoomSet(cardSet)}
                            type="checkbox"
                          />
                          <span>{cardSet}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
                <button className="btn btn-primary mt-2" onClick={() => void createGame()} type="button">
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
                <button className="btn btn-success mt-2" onClick={() => void joinGame()} type="button">
                  Join room
                </button>
              </div>
            </div>

            {statusText ? <div className="status-text mt-3">{statusText}</div> : null}
            {errorText ? <div className="error-text mt-2">{errorText}</div> : null}
          </div>
        </section>
      </main>
    );
  }

  // ── Game-over screen ───────────────────────────────────────────────────────
  if (screen === "gameover") {
    return (
      <main className="app-shell container-xl py-3">
        <section className="card border-0 bg-panel">
          <div className="card-body text-center py-5">
            <h1 className="app-title mb-3">Game over</h1>
            <p className="turn-banner mb-4">
              <span className="winner-name">{state?.winner || "Unknown player"}</span> wins!
            </p>
            <div className="d-flex justify-content-center gap-3">
              <button className="btn btn-primary" onClick={() => void createGame()} type="button">
                Play again
              </button>
              <button className="btn btn-outline-light" onClick={leaveSession} type="button">
                Return to lobby
              </button>
            </div>
            {errorText ? <div className="error-text mt-3">{errorText}</div> : null}
          </div>
        </section>
        <div className="top-icon-btns">
          <button className="log-icon-btn" onClick={() => setShowLog(true)} title="Game log" type="button">
            🗒
          </button>
          <button className="leave-icon-btn" onClick={leaveSession} title="Leave game" type="button">
            🚪
          </button>
        </div>
        {showLog ? <GameLog logLines={state?.log || []} onClose={() => setShowLog(false)} /> : null}
      </main>
    );
  }

  // ── Game screen ────────────────────────────────────────────────────────────
  return (
    <main className="app-shell container-xl py-3">
      <div className="row g-3">
        <div className="col-12">
          <section className="card border-0 bg-panel">
            <div className="card-body">
              <div className="d-flex flex-wrap gap-2 align-items-center justify-content-between">
                <div>
                  <div className="section-title mb-1">Game status</div>
                  <div className="turn-banner">
                    {isWaitingForOpponent
                      ? `Waiting for second player. Share code ${state!.invite_code}.`
                      : state!.pending_mindbug
                        ? state!.pending_mindbug.response_required_from_viewer
                          ? `Respond to ${state!.pending_mindbug.acting_player_name}'s ${parseCardLabel(state!.pending_mindbug.card_label).name}.`
                          : `Waiting for ${state!.pending_mindbug.responding_player_name} to answer the Mindbug prompt.`
                        : state!.pending_defense
                          ? state!.pending_defense.response_required_from_viewer
                            ? `Defend against ${state!.pending_defense.attacking_player_name}'s ${parseCardLabel(state!.pending_defense.attacker_label).name}.`
                            : `Waiting for ${state!.pending_defense.defending_player_name} to choose a blocker or lose 1 life.`
                          : state!.pending_card_action
                            ? state!.pending_card_action.response_required_from_viewer
                              ? `Resolve ${pendingCardActionName}'s action.`
                              : `Waiting for ${state!.pending_card_action.responding_player_name} to resolve ${pendingCardActionName}'s action.`
                            : state!.pending_defeated_ordering
                              ? state!.pending_defeated_ordering.response_required_from_viewer
                                ? "Choose the order of DEFEATED effects."
                                : `Waiting for ${state!.pending_defeated_ordering.responding_player_name} to choose DEFEATED action order.`
                              : state!.is_viewer_turn
                                ? "Your turn."
                                : `Waiting for ${state!.turn_player}.`}
                  </div>
                </div>
                {state!.pending_defense?.response_required_from_viewer ? (
                  <div className="d-flex flex-wrap gap-2 align-items-center">
                    <button className="btn btn-outline-light" onClick={() => void defendWithSelectedBlocker()} type="button">
                      Block with selected creature
                    </button>
                    <button className="btn btn-warning" onClick={() => void takeLifeLoss()} type="button">
                      Lose 1 life
                    </button>
                  </div>
                ) : null}
              </div>
              {statusText ? <div className="status-text mt-2">{statusText}</div> : null}
              {errorText ? <div className="error-text mt-2">{errorText}</div> : null}
            </div>
          </section>
        </div>

        {!isWaitingForOpponent && viewer ? (
          <>
            <div className="col-12">
              <BoardZone
                title={opponent?.name || state!.opponent_player_name || "Opponent"}
                player={opponent || { player_index: 1, name: state!.opponent_player_name || "Opponent", lives: 0, mindbugs_remaining: 0, hand_count: 0, draw_count: 0, discard_count: 0, battlefield: [], discard: [], hand: [] }}
                battlefieldMode={canAnswerDefense || hasBlockingChoiceModal ? "readonly" : "defender"}
                selectedBattlefieldIndex={canAnswerDefense && !hasBlockingChoiceModal ? selectedDefenderIndex : null}
                onSelectBattlefield={canAnswerDefense || hasBlockingChoiceModal ? undefined : (index) => toggleSelected("defender", index)}
                onPreview={(label) => setPreviewCardLabel(label)}
                animatedDiscardIndices={animatedCards.opponentDiscard}
                animatedBattlefieldStolenIndices={animatedCards.opponentBattlefieldStolen}
              />
            </div>
            <div className="col-12">
              <BoardZone
                title={`${viewer.name}${state!.is_viewer_turn ? " (your turn)" : ""}`}
                player={viewer}
                active={state!.is_viewer_turn}
                battlefieldMode={hasBlockingChoiceModal ? "readonly" : canAnswerDefense ? "defender" : "attacker"}
                selectedBattlefieldIndex={hasBlockingChoiceModal ? null : canAnswerDefense ? selectedDefenderIndex : selectedAttackerIndex}
                onSelectBattlefield={hasBlockingChoiceModal ? undefined : (index) => toggleSelected(canAnswerDefense ? "defender" : "attacker", index)}
                onPreview={(label) => setPreviewCardLabel(label)}
                animatedDiscardIndices={animatedCards.viewerDiscard}
                animatedBattlefieldStolenIndices={animatedCards.viewerBattlefieldStolen}
              />
            </div>
            <div className="col-12">
              <section className="card border-0 bg-panel">
                <div className="card-body">
                  <div className="row g-3 align-items-end">
                    <div className="col-md-4">
                      <button className="btn btn-primary w-100" disabled={!canAct} onClick={() => void playSelectedCard()} type="button">
                        Play selected hand card
                      </button>
                    </div>
                    <div className="col-md-4">
                      <div className="d-flex gap-2 align-items-center">
                        <button className="btn btn-outline-light flex-grow-1" disabled={!canAct} onClick={() => void attackSelected()} type="button">
                          Attack with selected board card
                        </button>
                        <div className="info-icon-wrapper">
                          <span className="info-icon">ⓘ</span>
                          <div className="info-tooltip-popup">
                            When your attacker has <span className="chip">HUNTER</span>, you can select a target.
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="col-md-4">
                      {canManuallyEndTurn ? (
                        <button className="btn btn-success w-100 mb-2" onClick={() => void endTurn()} type="button">
                          End turn
                        </button>
                      ) : null}
                      <div className="selection-box">{selectionText}</div>
                    </div>
                  </div>
                </div>
              </section>
            </div>
            <div className="col-12">
              <section className="card border-0 bg-panel">
                <div className="card-body">
                  <HandPanel
                    cards={hand}
                    selectedIndex={hasBlockingChoiceModal ? null : selectedHandIndex}
                    selectable={!hasBlockingChoiceModal}
                    onSelect={(index) => toggleSelected("hand", index)}
                    onPreview={(label) => setPreviewCardLabel(label)}
                    animatedIndices={animatedCards.viewerHand}
                  />
                </div>
              </section>
            </div>
          </>
        ) : null}
      </div>

      {canAnswerMindbug && isMindbugModalHidden ? (
        <div className="choice-modal-toggle">
          <button className="btn btn-outline-light btn-sm" onClick={reopenMindbugModal} type="button">
            Show prompt
          </button>
        </div>
      ) : null}
      {canAnswerCardAction && isChoiceModalHidden ? (
        <div className="choice-modal-toggle">
          <button className="btn btn-outline-light btn-sm" onClick={reopenChoiceModal} type="button">
            Show choice
          </button>
        </div>
      ) : null}
      {hasBlockingMindbugModal ? (
        <PendingMindbugModal
          cardLabel={state?.pending_mindbug?.card_label || ""}
          onUseMindbug={() => void answerMindbug(true)}
          onDecline={() => void answerMindbug(false)}
          onHide={hideMindbugModal}
        />
      ) : null}
      {hasBlockingChoiceModal ? (
        <PendingCardActionModal
          pending={state?.pending_card_action || null}
          cards={pendingCardActionPool}
          selectedIndices={selectedChoiceIndices}
          onToggle={toggleChoiceIndex}
          onConfirm={() => void resolveCardActionChoice()}
          onHide={hideChoiceModal}
        />
      ) : null}
      {canAnswerDefeatedOrdering && isDefeatedOrderingModalHidden ? (
        <div className="choice-modal-toggle">
          <div className="choice-modal-toggle-text">
            Choose DEFEATED action order
          </div>
          <button className="btn btn-outline-light btn-sm" onClick={() => setIsDefeatedOrderingModalHidden(false)} type="button">
            Show choice
          </button>
        </div>
      ) : null}
      {hasBlockingDefeatedOrderingModal && state?.pending_defeated_ordering ? (
        <DefeatedOrderingModal
          pending={state.pending_defeated_ordering}
          orderedIndices={defeatedOrderingIndices}
          onSelect={selectDefeatedOrder}
          onReset={resetDefeatedOrder}
          onConfirm={() => void confirmDefeatedOrdering()}
          onHide={() => setIsDefeatedOrderingModalHidden(true)}
        />
      ) : null}
      <CardPreviewModal label={previewCardLabel} onClose={() => setPreviewCardLabel(null)} />
      <div className="top-icon-btns">
        <button className="card-browser-icon-btn" onClick={() => setShowCardBrowser(true)} title="Card pool" type="button">
          🃏
        </button>
        <button className="log-icon-btn" onClick={() => setShowLog(true)} title="Game log" type="button">
          🗒
        </button>
        <button className="surrender-icon-btn" onClick={() => setShowSurrenderConfirm(true)} title="Surrender" type="button">
        <span role="img" aria-label="White flag" style={{ fontSize: '22px', marginRight: '4px' }}>
          🏳️
        </span>
        </button>
        <button className="leave-icon-btn" onClick={() => setShowLeaveConfirm(true)} title="Leave game" type="button">
          🚪
        </button>
      </div>
      {showSurrenderConfirm ? (
        <div className="overlay" onClick={() => setShowSurrenderConfirm(false)}>
          <div className="overlay-card surrender-confirm-modal" onClick={e => e.stopPropagation()}>
            <p>Surrender and let your opponent win?</p>
            <div className="surrender-confirm-btns">
              <button className="btn btn-danger btn-sm" onClick={() => void confirmSurrender()} type="button">Surrender</button>
              <button className="btn btn-outline-light btn-sm" onClick={() => setShowSurrenderConfirm(false)} type="button">Cancel</button>
            </div>
          </div>
        </div>
      ) : null}
      {showLeaveConfirm ? (
        <div className="overlay" onClick={() => setShowLeaveConfirm(false)}>
          <div className="overlay-card surrender-confirm-modal" onClick={e => e.stopPropagation()}>
            <p>Leave the game?</p>
            <div className="surrender-confirm-btns">
              <button className="btn btn-danger btn-sm" onClick={() => { setShowLeaveConfirm(false); leaveSession(); }} type="button">Leave</button>
              <button className="btn btn-outline-light btn-sm" onClick={() => setShowLeaveConfirm(false)} type="button">Cancel</button>
            </div>
          </div>
        </div>
      ) : null}
      {showCardBrowser && state ? (
        <CardBrowserModal
          cardPoolBySet={state.card_pool_by_set}
          selectedSets={state.selected_sets}
          onClose={() => setShowCardBrowser(false)}
        />
      ) : null}
      {showLog ? <GameLog logLines={state?.log || []} onClose={() => setShowLog(false)} /> : null}
    </main>
  );
}
