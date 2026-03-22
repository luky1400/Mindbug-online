import { cardImageUrl, parseCardLabel, strengthClassName } from "../utils/cards";

type CardTileSize = "compact" | "medium" | "large";

interface CardTileProps {
  label: string;
  selected?: boolean;
  clickable?: boolean;
  onClick?: () => void;
  onDoubleClick?: () => void;
  size?: CardTileSize;
  showStrength?: boolean;
}

export function CardTile({
  label,
  selected = false,
  clickable = false,
  onClick,
  onDoubleClick,
  size = "compact",
  showStrength = false
}: CardTileProps) {
  const parsed = parseCardLabel(label);
  const sizeClass = size === "large" ? "card-tile-large" : size === "medium" ? "card-tile-medium" : "";
  const selectableClass = clickable ? "card-tile-selectable" : "";
  const selectedClass = selected ? "card-tile-selected" : "";

  return (
    <button
      className={`card-tile ${sizeClass} ${selectableClass} ${selectedClass}`}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      type="button"
    >
      {showStrength ? (
        <span className={`strength-tag strength-${strengthClassName(label)}`}>{parsed.strengthText}</span>
      ) : null}
      <img
        className="card-image"
        src={cardImageUrl(label)}
        alt={label}
        onError={(event) => {
          const img = event.currentTarget;
          img.style.display = "none";
        }}
      />
      <div className="card-label">
        <div className="card-name">{parsed.name}</div>
        {parsed.details ? <div className="card-details">{parsed.details}</div> : null}
      </div>
    </button>
  );
}
