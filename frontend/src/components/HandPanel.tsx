import { useMemo, useState } from "react";
import { CardTile } from "./CardTile";

interface HandPanelProps {
  cards: string[];
  selectedIndex: number | null;
  onSelect: (index: number) => void;
  onPreview: (label: string) => void;
}

export function HandPanel({ cards, selectedIndex, onSelect, onPreview }: HandPanelProps) {
  const [expanded, setExpanded] = useState(false);
  const handTitle = useMemo(() => (expanded ? "Hand (expanded)" : "Hand (compact)"), [expanded]);

  return (
    <div className="panel-section">
      <div className="d-flex align-items-center justify-content-between mb-2 gap-2">
        <h3 className="section-title m-0">{handTitle}</h3>
        <button
          className="btn btn-sm btn-outline-light"
          onClick={() => setExpanded((value) => !value)}
          type="button"
        >
          {expanded ? "Collapse Hand" : "Expand Hand"}
        </button>
      </div>
      <p className="section-help">
        Click to select a card for play. Double click card for larger readable preview.
      </p>
      <div className={`hand-grid ${expanded ? "hand-grid-expanded" : "hand-grid-compact"}`}>
        {cards.length === 0 ? (
          <div className="placeholder">No cards</div>
        ) : (
          cards.map((label, index) => (
            <CardTile
              key={`${label}-${index}`}
              label={label}
              selected={selectedIndex === index}
              clickable
              size={expanded ? "large" : "medium"}
              onClick={() => onSelect(index)}
              onDoubleClick={() => onPreview(label)}
            />
          ))
        )}
      </div>
    </div>
  );
}
