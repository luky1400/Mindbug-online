## Brief Author’s Notes

- Game rules - [English rules](https://mindbug.me/wp-content/uploads/2023/08/mindbug-rulebook-ENGLISH-small.pdf), [Czech rules](https://www.rexhry.cz/storage/instructions/mb.rulebook.v3.cze_.web_.pdf)
- Create room lets the host choose which sets are used for that room. First Contact is always selected and cannot be unchecked, while the remaining CardSet values can be enabled. The selected sets are sent in the create-room request, stored on the room, used when the game starts, and shown in the UI in both the room metadata and room status area.
- Rooms are stored only in memory, so if the host server restarts, the game is lost.
- In `_select_cards_for_game()`, after selecting game cards, the remaining cards from the card pool are cloned, shuffled, and stored in `self.unused_pile`
- 2 main action functions: play_card, attack - resolved plays and attacks automatically trigger end_turn()
- trigger_play/attack/defeated_action() functions handle trigger of one time actions.
- funciton apply_ongoing_effect() enables recalculation of ongoing effects after each action (e.g. in the beginning of the turn, combat between 2 creatures, etc.)
- Cards are not allowed for selection for play, attack or defense when they are not eligible.
- TOUGH cards have `TOUGH` badge in the top-right + badges of keywords obtaioned from ongoing effects are visibale as well.
- Dynamic badges of special effects only appear when the is actually gained from an effect, not when it is native on the card (e.g. Lone Yeti, Mummy Cat, Snail Thrower effect, Ram Hopper ).
- App.tsx: the multiplayer client clears selections immediately when a defense response is sent
- `Shark_dog():`
  1. HUNTER target resolved early (stored as `hunter_defender`)
  2. ATTACK action fires → sets `_pending_card_action_choice`
  3. Stores `_pending_attack_continuation` with attacker + defender refs → **returns**
  4. Player calls `resolve_pending_card_action()` → choice resolves, Shark Dog defeats a creature
  5. `_continue_attack_after_action_resolution()` runs:
    - If HUNTER target was destroyed → "Combat is cancelled" → `_finalize_attack_action` (handles FRENZY)
    - If HUNTER target survived → `_resolve_combat()` proceeds normally
- When Compost Dragon is stolen by Mindbug and its PLAY action auto-resolves (1 card in discard), _apply_compost_dragon_choice used auto_end_after_play as a proxy for "was stolen by Mindbug". But in the auto-resolve path, the correction of auto_end_after_play = False never ran because _pending_card_action_choice was never set.
  - Fix: Added _play_is_stolen_by_mindbug flag on the Game, set before trigger_action and cleared after. _apply_compost_dragon_choice now checks both auto_end_after_play and this flag, so it works correctly in both the auto-resolve and pending-choice paths.

