interface GameOverModalProps {
  visible: boolean;
  winner: string;
  onNewGame: () => void;
  onClose: () => void;
}

export function GameOverModal({ visible, winner, onNewGame, onClose }: GameOverModalProps) {
  if (!visible) return null;
  return (
    <div className="overlay">
      <div className="overlay-card">
        <h2 className="mb-2">Game over</h2>
        <p className="mb-3">
          <span className="winner-name">{winner || "Unknown player"}</span> wins.
        </p>
        <div className="d-flex justify-content-center gap-2">
          <button className="btn btn-primary" onClick={onNewGame} type="button">
            Start new game
          </button>
          <button className="btn btn-outline-light" onClick={onClose} type="button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
