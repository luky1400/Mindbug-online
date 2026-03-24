import type { PendingCardActionState } from "../types/game";
import { CardTile } from "./CardTile";

interface PendingCardActionModalProps {
  pending: PendingCardActionState | null;
  cards: string[];
  selectedIndices: number[];
  onToggle: (index: number) => void;
  onConfirm: () => void;
  onHide: () => void;
}

function getZoneLabel(zone: PendingCardActionState["selection_zone"]): string {
  if (zone === "discard") return "discard pile";
  if (zone === "battlefield") return "battlefield";
  return "hand";
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

  const selectionHelp =
    pending.min_choices === pending.max_choices
      ? `Select exactly ${pending.min_choices} card${pending.min_choices === 1 ? "" : "s"}.`
      : `Select between ${pending.min_choices} and ${pending.max_choices} cards.`;

  return (
    <div className="overlay overlay-choice">
      <div className="overlay-card choice-overlay-card" onClick={(event) => event.stopPropagation()}>
        <h3 className="mb-2">Resolve {pending.source_card_label}</h3>
        <div className="cards-row justify-content-center mb-3">
          <CardTile
            label={pending.source_card_label}
            size="large"
          />
        </div>
        <p className="section-help mb-2">
          Choose from {pending.selection_owner_name}'s {getZoneLabel(pending.selection_zone)}.
        </p>
        <p className="section-help mb-3">{selectionHelp}</p>
        <div className="cards-row justify-content-center">
          {pending.eligible_indices.map((index) => (
            <CardTile
              key={`${cards[index]}-${index}`}
              label={cards[index]}
              selected={selectedIndices.includes(index)}
              clickable
              size="medium"
              onClick={() => onToggle(index)}
            />
          ))}
        </div>
        <div className="selection-box mt-3">
          Selected: {selectedIndices.length}/{pending.max_choices}
        </div>
        <div className="d-flex justify-content-end gap-2 mt-3">
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
