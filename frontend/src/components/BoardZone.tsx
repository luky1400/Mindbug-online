import { useState } from "react";
import type { PlayerState } from "../types/game";
import { CardTile } from "./CardTile";
import { DiscardPileModal } from "./DiscardPileModal";

interface BoardZoneProps {
  title: string;
  player: PlayerState;
  active?: boolean;
  battlefieldMode: "attacker" | "defender" | "readonly";
  selectedBattlefieldIndex: number | null;
  onSelectBattlefield?: (index: number) => void;
  onPreview?: (label: string) => void;
  animatedDiscardIndices?: Set<number>;
  animatedBattlefieldStolenIndices?: Set<number>;
}

export function BoardZone({
  title,
  player,
  active = false,
  battlefieldMode,
  selectedBattlefieldIndex,
  onSelectBattlefield,
  onPreview,
  animatedBattlefieldStolenIndices
}: BoardZoneProps) {
  const battlefieldClickable = battlefieldMode !== "readonly";
  const [showDiscardModal, setShowDiscardModal] = useState(false);

  return (
    <>
      <section className={`zone card border-0 ${active ? "zone-active" : ""}`}>
        <div className="card-body">
          <h2 className="zone-title">{title}</h2>
          <div className="board-zone-layout">
            <div className="board-zone-sidebar">
              <div className="sidebar-stats">
                <div className="stat-item stat-lives">
                  <span className="stat-value">{player.lives}</span>
                  <span className="stat-label">Lives</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{player.mindbugs_remaining}</span>
                  <span className="stat-label">Mindbugs</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{player.hand_count}</span>
                  <span className="stat-label">Hand</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{player.draw_count}</span>
                  <span className="stat-label">Draw</span>
                </div>
              </div>
              <button
                className={`discard-pile-btn ${player.discard_count === 0 ? "discard-pile-btn-empty" : ""}`}
                onClick={player.discard_count > 0 ? () => setShowDiscardModal(true) : undefined}
                title={player.discard_count > 0 ? "View discard pile" : "Discard pile is empty"}
                type="button"
                disabled={player.discard_count === 0}
              >
                <span className="discard-pile-icon">🪦</span>
                <span className="discard-pile-count">{player.discard_count}</span>
                <span className="discard-pile-label">Discard</span>
              </button>
            </div>
            <div className="board-zone-battlefield">
              <p className="section-title">
                Battlefield
                {battlefieldMode === "attacker" ? " (select attacker)" : ""}
                {battlefieldMode === "defender" ? " (select defender)" : ""}
              </p>
              <div className="cards-row">
                {player.battlefield.length === 0 ? (
                  <div className="placeholder">No cards</div>
                ) : (
                  player.battlefield.map((label, index) => (
                    <CardTile
                      key={`${label}-${index}`}
                      label={label}
                      size="medium"
                      selected={selectedBattlefieldIndex === index}
                      clickable={battlefieldClickable}
                      showStrength
                      showToughCharge
                      showAbilityBadges
                      showBattlefieldHighlight
                      onClick={battlefieldClickable ? () => onSelectBattlefield?.(index) : undefined}
                      onDoubleClick={() => onPreview?.(label)}
                      animationClass={animatedBattlefieldStolenIndices?.has(index) ? "card-tile-stolen-anim" : ""}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
      {showDiscardModal ? (
        <DiscardPileModal
          playerName={player.name}
          cards={player.discard}
          onClose={() => setShowDiscardModal(false)}
        />
      ) : null}
    </>
  );
}
