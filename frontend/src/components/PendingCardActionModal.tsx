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
  // Skip parts that only describe keywords (e.g. "<FRENZY>") or TOUGH state
  // (e.g. "tough:0 <TOUGH>") since those duplicate badges already shown on the
  // card image and are not meaningful action descriptions.
  const actionDescriptionParts = detailParts.filter(
    (part) => !part.startsWith("<") && !part.startsWith("tough:")
  );
  const actionHeading =
    actionDescriptionParts[actionDescriptionParts.length - 1] || "Choose";
  const stagedCardLabel = pending.staged_card_label;
  const isOptionChoice = pending.selection_zone === "options";
  const isChoiceReady =
    selectedIndices.length >= pending.min_choices &&
    selectedIndices.length <= pending.max_choices;

  return (
    <div className="overlay overlay-choice overlay-choice-centered">
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
          </div>
        ) : null}
        <div className="choice-options-grid mt-3">
          {pending.eligible_indices.map((index) => (
            <button
              key={`${cards[index]}-${index}`}
              className={`choice-preview-button ${isOptionChoice ? "choice-option-button" : ""} ${selectedIndices.includes(index) ? "choice-preview-selected" : ""}`}
              onClick={() => onToggle(index)}
              type="button"
            >
              {isOptionChoice ? (
                <span className="choice-option-label">{cards[index]}</span>
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
          <button
            className="btn btn-outline-light"
            onClick={onConfirm}
            type="button"
            disabled={!isChoiceReady}
          >
            Confirm choice
          </button>
        </div>
      </div>
    </div>
  );
}
