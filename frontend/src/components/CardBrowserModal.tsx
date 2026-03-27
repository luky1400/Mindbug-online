import { useState } from "react";
import type { CardPoolEntry, CardSet } from "../types/game";
import { CardTile } from "./CardTile";

interface CardBrowserModalProps {
  cardPoolBySet: { [set: string]: CardPoolEntry[] };
  selectedSets: CardSet[];
  onClose: () => void;
}

export function CardBrowserModal({ cardPoolBySet, selectedSets, onClose }: CardBrowserModalProps) {
  const [activeTab, setActiveTab] = useState<CardSet>(selectedSets[0]);

  return (
    <div className="overlay" onClick={onClose}>
      <div className="overlay-card card-browser-modal" onClick={(e) => e.stopPropagation()}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <h3 className="section-title m-0">Card Pool</h3>
          <button className="btn btn-outline-light btn-sm" onClick={onClose} type="button">
            Close
          </button>
        </div>
        <div className="card-browser-tabs">
          {selectedSets.map((set) => (
            <button
              key={set}
              className={`card-browser-tab${activeTab === set ? " active" : ""}`}
              onClick={() => setActiveTab(set)}
              type="button"
            >
              {set}
            </button>
          ))}
        </div>
        <div className="card-browser-grid">
          {(cardPoolBySet[activeTab] ?? []).map((entry) => (
            <div key={entry.label} className="card-browser-item">
              <span className="card-copies-badge">×{entry.copies}</span>
              <CardTile label={entry.label} size="medium" showStrength showAbilityBadges />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
