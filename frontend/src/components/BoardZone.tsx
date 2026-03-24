import type { PlayerState } from "../types/game";
import { CardTile } from "./CardTile";

interface BoardZoneProps {
  title: string;
  player: PlayerState;
  active?: boolean;
  battlefieldMode: "attacker" | "defender" | "readonly";
  selectedBattlefieldIndex: number | null;
  onSelectBattlefield?: (index: number) => void;
}

export function BoardZone({
  title,
  player,
  active = false,
  battlefieldMode,
  selectedBattlefieldIndex,
  onSelectBattlefield
}: BoardZoneProps) {
  const battlefieldClickable = battlefieldMode !== "readonly";

  return (
    <section className={`zone card border-0 ${active ? "zone-active" : ""}`}>
      <div className="card-body">
        <h2 className="zone-title">{title}</h2>
        <div className="d-flex flex-wrap gap-2 mb-3">
          <span className="chip">Lives: {player.lives}</span>
          <span className="chip">Mindbugs: {player.mindbugs_remaining}</span>
          <span className="chip">Hand: {player.hand_count}</span>
          <span className="chip">Draw: {player.draw_count}</span>
          <span className="chip">Discard: {player.discard_count}</span>
        </div>
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
                selected={selectedBattlefieldIndex === index}
                clickable={battlefieldClickable}
                showStrength
                showToughCharge
                showAbilityBadges
                showBattlefieldHighlight
                onClick={battlefieldClickable ? () => onSelectBattlefield?.(index) : undefined}
              />
            ))
          )}
        </div>
        <p className="section-title mt-3">Discard pile</p>
        <div className="cards-row">
          {player.discard.length === 0 ? (
            <div className="placeholder">No cards</div>
          ) : (
            player.discard.map((label, index) => (
              <CardTile key={`${label}-${index}`} label={label} />
            ))
          )}
        </div>
      </div>
    </section>
  );
}
