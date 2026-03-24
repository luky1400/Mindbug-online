import { cardImageUrl, getActiveAbilityBadges, hasActiveToughCharge, isHighlightedBattlefieldCard, parseCardLabel, strengthClassName } from "../utils/cards";

type CardTileSize = "compact" | "medium" | "large";

interface CardTileProps {
  label: string;
  selected?: boolean;
  clickable?: boolean;
  onClick?: () => void;
  onDoubleClick?: () => void;
  size?: CardTileSize;
  showStrength?: boolean;
  showToughCharge?: boolean;
  showAbilityBadges?: boolean;
  showBattlefieldHighlight?: boolean;
}

export function CardTile({
  label,
  selected = false,
  clickable = false,
  onClick,
  onDoubleClick,
  size = "compact",
  showStrength = false,
  showToughCharge = false,
  showAbilityBadges = false,
  showBattlefieldHighlight = false
}: CardTileProps) {
  const parsed = parseCardLabel(label);
  const sizeClass = size === "large" ? "card-tile-large" : size === "medium" ? "card-tile-medium" : "";
  const selectableClass = clickable ? "card-tile-selectable" : "";
  const selectedClass = selected ? "card-tile-selected" : "";
  const highlightClass = showBattlefieldHighlight && isHighlightedBattlefieldCard(label) ? "card-tile-battlefield-highlight" : "";
  const activeToughCharge = showToughCharge && hasActiveToughCharge(label);
  const activeAbilityBadges = showAbilityBadges ? getActiveAbilityBadges(label) : [];

  return (
    <button
      className={`card-tile ${sizeClass} ${selectableClass} ${selectedClass} ${highlightClass}`}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
      type="button"
    >
      {showStrength ? (
        <span className={`strength-tag strength-${strengthClassName(label)}`}>{parsed.strengthText}</span>
      ) : null}
      {activeToughCharge || activeAbilityBadges.length > 0 ? (
        <div className="card-status-badges">
          {activeToughCharge ? <span className="card-status-badge tough-tag">TOUGH</span> : null}
          {activeAbilityBadges.map((badge) => (
            <span
              key={badge}
              className={`card-status-badge ${badge === "FRENZY" ? "frenzy-tag" : ""} ${badge === "HUNTER" ? "hunter-tag" : ""} ${badge === "POISONOUS" ? "poisonous-tag" : ""} ${badge === "SNEAKY" ? "sneaky-tag" : ""}`}
            >
              {badge}
            </span>
          ))}
        </div>
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
