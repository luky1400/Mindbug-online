import { useState } from "react";
import type { PlayerState } from "../types/game";
import { CardTile } from "./CardTile";
import { DiscardPileModal } from "./DiscardPileModal";

type CombatEffect = "direct-hit" | "block-hit";
type DiscardGhost = {
  label: string;
  source: "battlefield" | "hand" | "unknown";
  defeated: boolean;
};

interface BoardZoneProps {
  title: string;
  player: PlayerState;
  active?: boolean;
  battlefieldMode: "attacker" | "defender" | "readonly";
  selectedBattlefieldIndex: number | null;
  onSelectBattlefield?: (index: number) => void;
  onPreview?: (label: string) => void;
  animatedDiscardIndices?: Set<number>;
  animatedDiscardDefeated?: boolean;
  discardGhosts?: DiscardGhost[];
  animatedBattlefieldStolenIndices?: Set<number>;
  animatedBattlefieldPlayedIndices?: Set<number>;
  animatedBattlefieldToughExhaustedIndices?: Set<number>;
  lifeDelta?: number;
  mindbugDelta?: number;
  drawPileDelta?: number;
  resurrectedCount?: number;
  combatEffect?: CombatEffect | null;
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
  animatedDiscardIndices,
  animatedDiscardDefeated = false,
  discardGhosts = [],
  animatedBattlefieldStolenIndices,
  animatedBattlefieldPlayedIndices,
  animatedBattlefieldToughExhaustedIndices,
  lifeDelta = 0,
  mindbugDelta = 0,
  drawPileDelta = 0,
  resurrectedCount = 0,
  combatEffect = null,
  disabledBattlefieldIndices,
  disabledBattlefieldTitle,
  pendingDefenseAttackerIndex
}: BoardZoneProps) {
  const battlefieldClickable = battlefieldMode !== "readonly";
  const [showDiscardModal, setShowDiscardModal] = useState(false);
  const hasAnimatedDiscard = Boolean(animatedDiscardIndices?.size);
  const discardAnimationClass = hasAnimatedDiscard
    ? animatedDiscardDefeated
      ? "discard-pile-btn-defeated-anim"
      : "discard-pile-btn-discarded-anim"
    : "";
  const hasEffectOverlay = Boolean(combatEffect || discardGhosts.length > 0 || resurrectedCount > 0);
  const formatDelta = (delta: number) => `${delta > 0 ? "+" : ""}${delta}`;

  return (
    <>
      <section className={`zone card border-0 ${active ? "zone-active" : ""} ${hasEffectOverlay ? "zone-effect-overlay" : ""}`}>
        <div className="card-body">
          <h2 className="zone-title">{title}</h2>
          <div className="board-zone-layout">
            <div className="board-zone-sidebar">
              <div className="stat-item stat-lives">
                <div className={`life-heart ${lifeDelta !== 0 ? lifeDelta > 0 ? "life-heart-gain-anim" : "life-heart-loss-anim" : ""}`} aria-label={`${player.lives} lives`}>
                  <span className="life-heart-number">{player.lives}</span>
                  {lifeDelta !== 0 ? (
                    <span className={`stat-delta ${lifeDelta > 0 ? "stat-delta-positive" : "stat-delta-negative"}`}>
                      {formatDelta(lifeDelta)}
                    </span>
                  ) : null}
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className={`mindbug-icon ${mindbugDelta < 0 ? "stat-icon-delta-anim" : ""}`} aria-label={`${player.mindbugs_remaining} mindbugs remaining`}>
                  <span className="icon-stat-number">{player.mindbugs_remaining}</span>
                  {mindbugDelta < 0 ? (
                    <span className="stat-delta stat-delta-negative">{formatDelta(mindbugDelta)}</span>
                  ) : null}
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className="hand-icon" aria-label={`${player.hand_count} cards in hand`}>
                  <span className="icon-stat-number">{player.hand_count}</span>
                </div>
              </div>
              <div className="stat-item stat-icon-only">
                <div className={`draw-pile-icon ${drawPileDelta > 0 ? "stat-icon-delta-anim" : ""}`} aria-label={`${player.draw_count} cards in draw pile`}>
                  <span className="icon-stat-number">{player.draw_count}</span>
                  {drawPileDelta > 0 ? (
                    <span className="stat-delta stat-delta-positive">{formatDelta(drawPileDelta)}</span>
                  ) : null}
                </div>
              </div>
              <button
                className={`discard-pile-btn ${player.discard_count === 0 ? "discard-pile-btn-empty" : ""} ${discardAnimationClass}`}
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
                    const animationClass = animatedBattlefieldStolenIndices?.has(index)
                      ? "card-tile-stolen-anim"
                      : animatedBattlefieldToughExhaustedIndices?.has(index)
                        ? "card-tile-tough-exhausted-anim"
                        : animatedBattlefieldPlayedIndices?.has(index)
                          ? "card-tile-played-anim"
                          : "";
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
                        animationClass={animationClass}
                      />
                    );
                  })
                )}
              </div>
            </div>
          </div>
          {combatEffect ? (
            <div className={`combat-effect combat-effect-${combatEffect}`} aria-live="polite">
              <span>{combatEffect === "direct-hit" ? "Direct hit" : "Clash"}</span>
            </div>
          ) : null}
          {discardGhosts.length > 0 ? (
            <div className="discard-ghost-layer" aria-hidden="true">
              {discardGhosts.map((ghost, index) => (
                <div
                  key={`${ghost.label}-${ghost.source}-${index}`}
                  className={`discard-ghost discard-ghost-${ghost.source} ${ghost.defeated ? "discard-ghost-defeated" : "discard-ghost-discarded"}`}
                >
                  <CardTile label={ghost.label} size="medium" />
                </div>
              ))}
            </div>
          ) : null}
          {resurrectedCount > 0 ? (
            <div className="resurrection-effect" aria-live="polite">
              <span>Resurrected +{resurrectedCount}</span>
            </div>
          ) : null}
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
