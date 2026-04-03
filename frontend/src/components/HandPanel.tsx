import { CardTile } from "./CardTile";

interface HandPanelProps {
  cards: string[];
  selectedIndex: number | null;
  selectable?: boolean;
  onSelect: (index: number) => void;
  onPreview: (label: string) => void;
  animatedIndices?: Set<number>;
}

export function HandPanel({ cards, selectedIndex, selectable = true, onSelect, onPreview, animatedIndices }: HandPanelProps) {
  return (
    <div className="hand-scroll">
      <div className="hand-row">
        {cards.length === 0 ? (
          <div className="placeholder">No cards</div>
        ) : (
          cards.map((label, index) => (
            <CardTile
              key={`${label}-${index}`}
              label={label}
              selected={selectedIndex === index}
              clickable={selectable}
              size="medium"
              onClick={selectable ? () => onSelect(index) : undefined}
              onDoubleClick={() => onPreview(label)}
              animationClass={animatedIndices?.has(index) ? "card-tile-draw-anim" : ""}
            />
          ))
        )}
      </div>
    </div>
  );
}
