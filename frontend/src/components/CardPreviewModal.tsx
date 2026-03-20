import { cardImageUrl, parseCardLabel } from "../utils/cards";

interface CardPreviewModalProps {
  label: string | null;
  onClose: () => void;
}

export function CardPreviewModal({ label, onClose }: CardPreviewModalProps) {
  if (!label) return null;
  const parsed = parseCardLabel(label);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="overlay-card card-preview-card" onClick={(event) => event.stopPropagation()}>
        <h3 className="mb-2">{parsed.name}</h3>
        <img
          className="preview-image"
          src={cardImageUrl(label)}
          alt={label}
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
        <div className="preview-strength">Strength: {parsed.strengthText}</div>
        {parsed.details ? <div className="preview-details">{parsed.details}</div> : null}
        <div className="d-flex justify-content-end mt-3">
          <button className="btn btn-outline-light" onClick={onClose} type="button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
