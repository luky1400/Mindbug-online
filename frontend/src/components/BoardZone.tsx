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
  disabledBattlefieldIndices?: Set<number>;
  disabledBattlefieldTitle?: string;
  pendingDefenseAttackerIndex?: number | null;
}

export function BoardZone({
  title,
  player,
  active = false,
  battlefieldMode,
  selectedBattlefieldIndex,
  onSelectBattlefield,
  onPreview,
  animatedBattlefieldStolenIndices,
  disabledBattlefieldIndices,
  disabledBattlefieldTitle,
  pendingDefenseAttackerIndex
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
              <div className="stat-item stat-lives">
                <div className="life-heart" aria-label={`${player.lives} lives`}>
                  <span className="life-heart-number">{player.lives}</span>
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className="mindbug-icon" aria-label={`${player.mindbugs_remaining} mindbugs remaining`}>
                  <span className="icon-stat-number">{player.mindbugs_remaining}</span>
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className="hand-icon" aria-label={`${player.hand_count} cards in hand`}>
                  <span className="icon-stat-number">{player.hand_count}</span>
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className="draw-pile-icon" aria-label={`${player.draw_count} cards in draw pile`}>
                  <span className="icon-stat-number">{player.draw_count}</span>
                </div>
              </div>
              <button
                className={`discard-pile-btn ${player.discard_count === 0 ? "discard-pile-btn-empty" : ""}`}
                onClick={player.discard_count > 0 ? () => setShowDiscardModal(true) : undefined}
                title={player.discard_count > 0 ? "View discard pile" : "Discard pile is empty"}
                type="button"
                disabled={player.discard_count === 0}
              >
                <div className="discard-icon" aria-label={`${player.discard_count} cards in discard pile`}>
                  <span className="discard-icon-number">{player.discard_count}</span>
                </div>
              </button>
            </div>
            <div className="board-zone-battlefield">
              <div className="cards-row battlefield-cards-row">
                {player.battlefield.length === 0 ? (
                  <div className="placeholder">No cards</div>
                ) : (
                  player.battlefield.map((label, index) => {
                    const isDisabled = battlefieldClickable && (disabledBattlefieldIndices?.has(index) ?? false);
                    return (
                      <CardTile
                        key={`${label}-${index}`}
                        label={label}
                        size="large"
                        selected={selectedBattlefieldIndex === index}
                        clickable={battlefieldClickable}
                        disabled={isDisabled}
                        disabledTitle={disabledBattlefieldTitle}
                        showStrength
                        showToughCharge
                        showAbilityBadges
                        showBattlefieldHighlight
                        pendingDefenseAttacker={pendingDefenseAttackerIndex === index}
                        onClick={battlefieldClickable && !isDisabled ? () => onSelectBattlefield?.(index) : undefined}
                        onDoubleClick={() => onPreview?.(label)}
                        animationClass={animatedBattlefieldStolenIndices?.has(index) ? "card-tile-stolen-anim" : ""}
                      />
                    );
                  })
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
