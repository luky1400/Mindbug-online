interface GameLogProps {
  logLines: string[];
}

export function GameLog({ logLines }: GameLogProps) {
  return (
    <section className="card border-0 bg-panel">
      <div className="card-body">
        <h3 className="section-title">Recent log</h3>
        <pre className="log-box">{logLines.length ? logLines.join("\n") : "-"}</pre>
      </div>
    </section>
  );
}
