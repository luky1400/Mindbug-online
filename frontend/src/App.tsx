import { useMemo, useState } from "react";
import { gameApi } from "./api/client";
import { ActionPanel } from "./components/ActionPanel";
import { BoardZone } from "./components/BoardZone";
import { CardPreviewModal } from "./components/CardPreviewModal";
import { GameLog } from "./components/GameLog";
import { GameOverModal } from "./components/GameOverModal";
import { HandPanel } from "./components/HandPanel";
import { TopBar } from "./components/TopBar";
import type { GameState } from "./types/game";
import { cardHasTag } from "./utils/cards";

type AttackMode = "direct" | "normal";

export function App() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [state, setState] = useState<GameState | null>(null);
  const [player1, setPlayer1] = useState("Player 1");
  const [player2, setPlayer2] = useState("Player 2");

  const [selectedHandIndex, setSelectedHandIndex] = useState<number | null>(null);
  const [selectedAttackerIndex, setSelectedAttackerIndex] = useState<number | null>(null);
  const [selectedDefenderIndex, setSelectedDefenderIndex] = useState<number | null>(null);
  const [pendingFrenzyAttack, setPendingFrenzyAttack] = useState<{ attackerIndex: number } | null>(null);

  const [useMindbug, setUseMindbug] = useState(false);
  const [hunterOverride, setHunterOverride] = useState(true);
  const [statusText, setStatusText] = useState("");
  const [errorText, setErrorText] = useState("");
  const [showGameOver, setShowGameOver] = useState(false);
  const [previewCardLabel, setPreviewCardLabel] = useState<string | null>(null);

  const turnPlayer = useMemo(
    () => state?.players.find((player) => player.name === state.turn_player) || null,
    [state]
  );
  const opponent = useMemo(
    () => state?.players.find((player) => player.name !== state.turn_player) || null,
    [state]
  );

  const turnHand = useMemo(() => {
    if (!state || !turnPlayer) return [];
    return state.turn_hand || turnPlayer.hand || [];
  }, [state, turnPlayer]);

  const gameOver = state?.game_state === "GAME_OVER";

  const metaText = useMemo(() => {
    if (!state || !gameId) return "No active game.";
    return `Game ${gameId} | Turn: ${state.turn_player} | State: ${state.game_state}${state.winner ? ` | Winner: ${state.winner}` : ""}`;
  }, [state, gameId]);

  const selectionText = `Hand: ${selectedHandIndex ?? "-"} | Attacker: ${selectedAttackerIndex ?? "-"} | Defender: ${selectedDefenderIndex ?? "-"}`;

  function normalizeSelections(nextState: GameState) {
    const nextTurnPlayer = nextState.players.find((player) => player.name === nextState.turn_player);
    const nextOpponent = nextState.players.find((player) => player.name !== nextState.turn_player);
    const nextHand = nextState.turn_hand || nextTurnPlayer?.hand || [];
    const nextBoard = nextTurnPlayer?.battlefield || [];
    const nextOpponentBoard = nextOpponent?.battlefield || [];

    if (selectedHandIndex !== null && (selectedHandIndex < 0 || selectedHandIndex >= nextHand.length)) {
      setSelectedHandIndex(null);
    }
    if (selectedAttackerIndex !== null && (selectedAttackerIndex < 0 || selectedAttackerIndex >= nextBoard.length)) {
      setSelectedAttackerIndex(null);
    }
    if (selectedDefenderIndex !== null && (selectedDefenderIndex < 0 || selectedDefenderIndex >= nextOpponentBoard.length)) {
      setSelectedDefenderIndex(null);
    }
    if (pendingFrenzyAttack && (pendingFrenzyAttack.attackerIndex < 0 || pendingFrenzyAttack.attackerIndex >= nextBoard.length)) {
      setPendingFrenzyAttack(null);
    }
  }

  function applyState(nextState: GameState) {
    normalizeSelections(nextState);
    setState(nextState);
    if (nextState.game_state === "GAME_OVER") {
      setShowGameOver(true);
    }
  }

  async function createGame() {
    setErrorText("");
    try {
      const response = await gameApi.createGame({
        player1: player1.trim() || "Player 1",
        player2: player2.trim() || "Player 2"
      });
      setGameId(response.game_id);
      setSelectedHandIndex(null);
      setSelectedAttackerIndex(null);
      setSelectedDefenderIndex(null);
      setPendingFrenzyAttack(null);
      setStatusText("Game created.");
      setShowGameOver(false);
      applyState(response.state);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function refreshState() {
    if (!gameId) {
      setErrorText("Create a game first.");
      return;
    }
    setErrorText("");
    try {
      const response = await gameApi.getState(gameId);
      applyState(response.state);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function maybeAutoEndTurnAfterAction(nextState: GameState, actionLabel: string) {
    if (!gameId) return;
    if (nextState.game_state === "GAME_OVER") {
      applyState(nextState);
      setStatusText(`${actionLabel} resolved. Game over.`);
      return;
    }
    const endResponse = await gameApi.endTurn(gameId);
    setSelectedHandIndex(null);
    setSelectedAttackerIndex(null);
    setSelectedDefenderIndex(null);
    setPendingFrenzyAttack(null);
    applyState(endResponse.state);
    setStatusText(`${actionLabel} resolved. Turn ended automatically.`);
  }

  async function playSelectedCard(forcedHandIndex: number | null = null) {
    if (!gameId) return setErrorText("Create a game first.");
    if (pendingFrenzyAttack) return setErrorText("Finish the pending FRENZY extra attack or end turn.");
    const handIndex = forcedHandIndex ?? selectedHandIndex;
    if (handIndex === null) return setErrorText("Select a hand card first.");

    setErrorText("");
    try {
      const response = await gameApi.playCard(gameId, {
        hand_index: handIndex,
        use_opponent_mindbug: useMindbug
      });
      await maybeAutoEndTurnAfterAction(response.state, "Play");
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function attackSelected(mode: AttackMode = "normal") {
    if (!gameId || !state || !turnPlayer) return setErrorText("Create a game first.");

    const attackerIndex = selectedAttackerIndex;
    const defenderIndex = mode === "direct" ? null : selectedDefenderIndex;
    if (attackerIndex === null) return setErrorText("Select an attacker first.");
    if (mode !== "direct" && defenderIndex === null) return setErrorText("Select a defender or use direct attack.");

    const attackerLabel = turnPlayer.battlefield[attackerIndex];
    const isHunter = cardHasTag(attackerLabel, "HUNTER");
    const isFrenzy = cardHasTag(attackerLabel, "FRENZY");

    if (isHunter && hunterOverride && mode !== "direct" && defenderIndex === null) {
      return setErrorText("For HUNTER override, select a defender target.");
    }
    if (pendingFrenzyAttack && attackerIndex !== pendingFrenzyAttack.attackerIndex) {
      return setErrorText("Use the same FRENZY attacker for the second attack, or end turn.");
    }

    setErrorText("");
    try {
      const response = await gameApi.attack(gameId, {
        attacker_index: attackerIndex,
        defender_index: defenderIndex,
        hunter_target_override: mode === "direct" ? false : hunterOverride
      });
      const turnPlayerAfter = response.state.players.find((player) => player.name === response.state.turn_player);
      const attackerStillAlive = attackerIndex < (turnPlayerAfter?.battlefield.length || 0);

      if (isFrenzy && !pendingFrenzyAttack && response.state.game_state !== "GAME_OVER" && attackerStillAlive) {
        setPendingFrenzyAttack({ attackerIndex });
        setSelectedAttackerIndex(attackerIndex);
        setSelectedDefenderIndex(null);
        applyState(response.state);
        setStatusText("FRENZY: attacker may attack one more time this turn.");
        return;
      }

      setPendingFrenzyAttack(null);
      await maybeAutoEndTurnAfterAction(response.state, mode === "direct" ? "Direct attack" : "Attack");
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  async function endTurn() {
    if (!gameId) return setErrorText("Create a game first.");
    setErrorText("");
    try {
      const response = await gameApi.endTurn(gameId);
      setSelectedHandIndex(null);
      setSelectedAttackerIndex(null);
      setSelectedDefenderIndex(null);
      setPendingFrenzyAttack(null);
      setStatusText("Turn ended.");
      applyState(response.state);
    } catch (error) {
      setErrorText((error as Error).message);
    }
  }

  function toggleSelected(
    type: "hand" | "attacker" | "defender",
    index: number
  ) {
    if (type === "hand") setSelectedHandIndex((current) => (current === index ? null : index));
    if (type === "attacker") setSelectedAttackerIndex((current) => (current === index ? null : index));
    if (type === "defender") setSelectedDefenderIndex((current) => (current === index ? null : index));
  }

  return (
    <main className="app-shell container-xl py-3">
      <TopBar
        player1={player1}
        player2={player2}
        onPlayer1Change={setPlayer1}
        onPlayer2Change={setPlayer2}
        onNewGame={createGame}
        onRefresh={refreshState}
        metaText={metaText}
        statusText={statusText}
        errorText={errorText}
      />

      <ActionPanel
        hasGame={Boolean(gameId)}
        disabled={Boolean(gameOver)}
        useMindbug={useMindbug}
        onUseMindbugChange={setUseMindbug}
        hunterOverride={hunterOverride}
        onHunterOverrideChange={setHunterOverride}
        selectionText={selectionText}
        onPlayCard={() => void playSelectedCard()}
        onAttack={() => void attackSelected("normal")}
        onDirectAttack={() => void attackSelected("direct")}
        onEndTurn={() => void endTurn()}
      />

      {state && turnPlayer && opponent ? (
        <div className="row g-3">
          <div className="col-12">
            <BoardZone
              title={`${opponent.name}`}
              player={opponent}
              battlefieldMode="defender"
              selectedBattlefieldIndex={selectedDefenderIndex}
              onSelectBattlefield={(index) => toggleSelected("defender", index)}
            />
          </div>
          <div className="col-12">
            <BoardZone
              title={`${turnPlayer.name} (on turn)`}
              player={turnPlayer}
              active
              battlefieldMode="attacker"
              selectedBattlefieldIndex={selectedAttackerIndex}
              onSelectBattlefield={(index) => toggleSelected("attacker", index)}
            />
          </div>
          <div className="col-12">
            <section className="card border-0 bg-panel">
              <div className="card-body">
                <HandPanel
                  cards={turnHand}
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
            <div className="placeholder">Create a game to see board state.</div>
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
