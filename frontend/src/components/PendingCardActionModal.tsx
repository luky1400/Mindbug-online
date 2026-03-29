import type { PendingCardActionState } from "../types/game";
import { cardImageUrl, parseCardLabel } from "../utils/cards";

interface PendingCardActionModalProps {
  pending: PendingCardActionState | null;
  cards: string[];
  selectedIndices: number[];
  onToggle: (index: number) => void;
  onConfirm: () => void;
  onHide: () => void;
}

export function PendingCardActionModal({
  pending,
  cards,
  selectedIndices,
  onToggle,
  onConfirm,
  onHide
}: PendingCardActionModalProps) {
  if (!pending?.response_required_from_viewer) return null;
  const details = parseCardLabel(pending.source_card_label).details;
  const detailParts = details
    .split("|")
    .map((part) => part.trim())
    .filter(Boolean);
  const actionHeading = details.includes("|")
    ? detailParts[detailParts.length - 1] || "Choose card"
    : details || "Choose card";
  const stagedCardLabel = pending.staged_card_label;
  const isOptionChoice = pending.selection_zone === "options";

  return (
    <div className="overlay overlay-choice">
      <div className="choice-overlay-content" onClick={(event) => event.stopPropagation()}>
        <h3 className="text-center mb-3">{actionHeading}</h3>
        {stagedCardLabel ? (
          <div className="text-center mb-3">
            <img
              className="preview-image choice-preview-image"
              src={cardImageUrl(stagedCardLabel)}
              alt={stagedCardLabel}
              onError={(event) => {
                event.currentTarget.style.display = "none";
              }}
            />
            <div className="mt-2">{parseCardLabel(stagedCardLabel).name}</div>
          </div>
        ) : null}
        <div className="choice-options-grid mt-3">
          {pending.eligible_indices.map((index) => (
            <button
              key={`${cards[index]}-${index}`}
              className={`choice-preview-button ${selectedIndices.includes(index) ? "choice-preview-selected" : ""}`}
              onClick={() => onToggle(index)}
              type="button"
            >
              {isOptionChoice ? (
                <span>{cards[index]}</span>
              ) : (
                <img
                  className="preview-image choice-preview-image"
                  src={cardImageUrl(cards[index])}
                  alt={cards[index]}
                  onError={(event) => {
                    event.currentTarget.style.display = "none";
                  }}
                />
              )}
            </button>
          ))}
        </div>
        <div className="selection-box mt-3 text-center">
          Selected: {selectedIndices.length}/{pending.max_choices}
        </div>
        <div className="d-flex justify-content-center gap-2 mt-3">
          <button className="btn btn-outline-secondary" onClick={onHide} type="button">
            Hide for now
          </button>
          <button className="btn btn-outline-light" onClick={onConfirm} type="button">
            Confirm choice
          </button>
        </div>
      </div>
    </div>
  );
}
