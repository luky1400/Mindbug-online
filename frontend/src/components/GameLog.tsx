interface GameLogProps {
  logLines: string[];
  onClose: () => void;
}

export function GameLog({ logLines, onClose }: GameLogProps) {
  return (
    <div className="overlay" onClick={onClose}>
      <div className="overlay-card log-popup-card" onClick={(event) => event.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="section-title m-0">Game logs</h3>
          <button className="btn btn-outline-light btn-sm" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <pre className="log-box log-box-tall">{logLines.length ? logLines.join("\n") : "-"}</pre>
      </div>
    </div>
  );
}
