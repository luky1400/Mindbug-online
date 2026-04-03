import { cardImageUrl } from "../utils/cards";

interface DiscardPileModalProps {
  playerName: string;
  cards: string[];
  onClose: () => void;
}

export function DiscardPileModal({ playerName, cards, onClose }: DiscardPileModalProps) {
  return (
    <div className="overlay overlay-choice overlay-choice-centered" onClick={onClose}>
      <div className="choice-overlay-content" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-center mb-3">{playerName}'s Discard Pile</h3>
        <div className="discard-modal-grid mt-3">
          {cards.map((label, index) => (
            <div key={`${label}-${index}`} className="discard-modal-card">
              <img
                className="discard-modal-image"
                src={cardImageUrl(label)}
                alt={label}
                onError={(event) => {
                  event.currentTarget.style.display = "none";
                }}
              />
            </div>
          ))}
        </div>
        <div className="d-flex justify-content-center mt-3">
          <button className="btn btn-outline-light" onClick={onClose} type="button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
