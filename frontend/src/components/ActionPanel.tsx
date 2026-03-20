interface ActionPanelProps {
  hasGame: boolean;
  disabled: boolean;
  useMindbug: boolean;
  onUseMindbugChange: (value: boolean) => void;
  hunterOverride: boolean;
  onHunterOverrideChange: (value: boolean) => void;
  selectionText: string;
  onPlayCard: () => void;
  onAttack: () => void;
  onDirectAttack: () => void;
  onEndTurn: () => void;
}

export function ActionPanel({
  hasGame,
  disabled,
  useMindbug,
  onUseMindbugChange,
  hunterOverride,
  onHunterOverrideChange,
  selectionText,
  onPlayCard,
  onAttack,
  onDirectAttack,
  onEndTurn
}: ActionPanelProps) {
  return (
    <section className="card border-0 bg-panel">
      <div className="card-body">
        <div className="row g-3 align-items-end">
          <div className="col-md-4">
            <h3 className="section-title">Play</h3>
            <button className="btn btn-primary w-100 mb-2" disabled={!hasGame || disabled} onClick={onPlayCard} type="button">
              Play selected hand card
            </button>
            <div className="form-check">
              <input
                id="useMindbug"
                className="form-check-input"
                type="checkbox"
                checked={useMindbug}
                disabled={!hasGame || disabled}
                onChange={(event) => onUseMindbugChange(event.target.checked)}
              />
              <label htmlFor="useMindbug" className="form-check-label text-light">
                Opponent uses Mindbug
              </label>
            </div>
          </div>
          <div className="col-md-4">
            <h3 className="section-title">Attack</h3>
            <div className="d-grid gap-2">
              <button className="btn btn-outline-light" disabled={!hasGame || disabled} onClick={onAttack} type="button">
                Attack selected defender
              </button>
              <button className="btn btn-outline-warning" disabled={!hasGame || disabled} onClick={onDirectAttack} type="button">
                Direct attack
              </button>
            </div>
            <div className="form-check mt-2">
              <input
                id="hunterOverride"
                className="form-check-input"
                type="checkbox"
                checked={hunterOverride}
                disabled={!hasGame || disabled}
                onChange={(event) => onHunterOverrideChange(event.target.checked)}
              />
              <label htmlFor="hunterOverride" className="form-check-label text-light">
                Use HUNTER target override
              </label>
            </div>
          </div>
          <div className="col-md-4">
            <h3 className="section-title">Turn</h3>
            <button className="btn btn-success w-100 mb-2" disabled={!hasGame || disabled} onClick={onEndTurn} type="button">
              End turn
            </button>
            <div className="selection-box">{selectionText}</div>
          </div>
        </div>
      </div>
    </section>
  );
}
