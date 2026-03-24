import { cardImageUrl } from "../utils/cards";

interface PendingMindbugModalProps {
  cardLabel: string;
  onUseMindbug: () => void;
  onDecline: () => void;
  onHide: () => void;
}

export function PendingMindbugModal({
  cardLabel,
  onUseMindbug,
  onDecline,
  onHide
}: PendingMindbugModalProps) {
  return (
    <div className="overlay overlay-choice">
      <div className="mindbug-overlay-content" onClick={(event) => event.stopPropagation()}>
        <img
          className="preview-image mindbug-overlay-image"
          src={cardImageUrl(cardLabel)}
          alt={cardLabel}
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
        <div className="d-flex justify-content-center gap-2 mt-3">
          <button className="btn btn-outline-secondary" onClick={onHide} type="button">
            Hide for now
          </button>
          <button className="btn btn-outline-light" onClick={onDecline} type="button">
            Decline
          </button>
          <button className="btn btn-warning" onClick={onUseMindbug} type="button">
            Use Mindbug
          </button>
        </div>
      </div>
    </div>
  );
}
