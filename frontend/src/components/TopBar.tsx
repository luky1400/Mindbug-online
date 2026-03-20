interface TopBarProps {
  player1: string;
  player2: string;
  onPlayer1Change: (value: string) => void;
  onPlayer2Change: (value: string) => void;
  onNewGame: () => void;
  onRefresh: () => void;
  metaText: string;
  statusText: string;
  errorText: string;
}

export function TopBar({
  player1,
  player2,
  onPlayer1Change,
  onPlayer2Change,
  onNewGame,
  onRefresh,
  metaText,
  statusText,
  errorText
}: TopBarProps) {
  return (
    <section className="card border-0 bg-panel">
      <div className="card-body">
        <div className="d-flex flex-wrap align-items-end gap-2 mb-3">
          <h1 className="app-title m-0 me-2">Mindbug Web</h1>
          <div className="d-flex flex-wrap align-items-center gap-2">
            <label className="text-light">
              Player 1
              <input
                className="form-control form-control-sm mt-1"
                value={player1}
                onChange={(event) => onPlayer1Change(event.target.value)}
              />
            </label>
            <label className="text-light">
              Player 2
              <input
                className="form-control form-control-sm mt-1"
                value={player2}
                onChange={(event) => onPlayer2Change(event.target.value)}
              />
            </label>
          </div>
          <button className="btn btn-primary ms-auto" onClick={onNewGame} type="button">
            New game
          </button>
          <button className="btn btn-outline-light" onClick={onRefresh} type="button">
            Refresh
          </button>
        </div>
        <div className="meta-text">{metaText}</div>
        {statusText ? <div className="status-text">{statusText}</div> : null}
        {errorText ? <div className="error-text">{errorText}</div> : null}
      </div>
    </section>
  );
}
