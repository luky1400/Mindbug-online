from base_classes import Card, DrawPile, Game
from unittest.mock import patch
from cards import (
    Boar_zooka,
    Chameleon_sniper,
    Explosive_toad,
    Ferret_bomber,
    Harpy_mother,
    Knightmare,
    Luchataur,
    Plated_scorpion,
    Shield_bugs,
    Snail_hydra,
    Strange_barrel,
    Tiger_squirrel,
)
from enums import GameState


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
    )
    game.start_game()
    return game


def _attack_and_defend(game: Game, attacker_index: int = 0, defender_index: int | None = 0) -> None:
    game.attack(attacker_index=attacker_index)
    game.defend(defender_index=defender_index)


def test_defeated_explosive_toad_defeats_an_enemy_creature() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    explosive_toad = Explosive_toad()
    enemy_creature = Luchataur()

    player.cards_laid_out = [explosive_toad]
    opponent.cards_laid_out = [enemy_creature]
    player.hand = [Chameleon_sniper()]
    opponent.hand = [Tiger_squirrel()]

    game._destroy_creature(player, explosive_toad)

    assert explosive_toad in player.discard_pile
    assert explosive_toad not in player.cards_laid_out
    assert enemy_creature in opponent.discard_pile
    assert enemy_creature not in opponent.cards_laid_out


def test_defeated_explosive_toad_lets_owner_choose_enemy_creature_to_defeat() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    explosive_toad = Explosive_toad()
    enemy_creature_1 = Luchataur()
    enemy_creature_2 = Shield_bugs()

    player.cards_laid_out = [explosive_toad]
    opponent.cards_laid_out = [enemy_creature_1, enemy_creature_2]
    player.hand = [Chameleon_sniper()]
    opponent.hand = [Tiger_squirrel()]

    game._destroy_creature(player, explosive_toad)
    game.resolve_pending_card_action([0])

    assert enemy_creature_1 in opponent.discard_pile
    assert enemy_creature_1 not in opponent.cards_laid_out
    assert enemy_creature_2 in opponent.cards_laid_out


def test_defending_explosive_toad_lets_owner_choose_enemy_creature_to_defeat() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    attacker = Luchataur()
    other_enemy = Tiger_squirrel()
    explosive_toad = Explosive_toad()

    attacker_owner.cards_laid_out = [attacker, other_enemy]
    defender_owner.cards_laid_out = [explosive_toad]
    attacker_owner.hand = [Chameleon_sniper()]
    defender_owner.hand = [Shield_bugs()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_card_action_choice is not None
    assert game._pending_card_action_choice.action_key == "explosive_toad"
    assert game._pending_card_action_choice.responding_player_index == game.players.index(
        defender_owner
    )
    assert game._pending_card_action_choice.selection_owner_index == game.players.index(
        attacker_owner
    )
    assert game._pending_combat_finalization is not None

    game.resolve_pending_card_action([1])

    assert other_enemy in attacker_owner.discard_pile
    assert attacker in attacker_owner.cards_laid_out
    assert explosive_toad in defender_owner.discard_pile
    assert game._pending_combat_finalization is None


def test_defending_explosive_toad_auto_defeats_only_enemy_creature() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    attacker = Luchataur()
    explosive_toad = Explosive_toad()

    attacker_owner.cards_laid_out = [attacker]
    defender_owner.cards_laid_out = [explosive_toad]
    attacker_owner.hand = [Chameleon_sniper()]
    defender_owner.hand = [Shield_bugs()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_card_action_choice is None
    assert game._pending_combat_finalization is None
    assert attacker in attacker_owner.discard_pile
    assert explosive_toad in defender_owner.discard_pile


def test_defeated_harpy_mother_takes_control_of_up_to_2_weak_enemy_creatures() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    harpy_mother = Harpy_mother()
    weak_enemy_1 = Chameleon_sniper()
    weak_enemy_2 = Ferret_bomber()
    strong_enemy = Luchataur()

    player.cards_laid_out = [harpy_mother]
    player.hand = [Chameleon_sniper()]  # Keep game active while choice is pending.
    opponent.cards_laid_out = [weak_enemy_1, weak_enemy_2, strong_enemy]

    _attack_and_defend(game, attacker_index=0, defender_index=2)
    # Eligible indices are [0, 1] (weak_enemy_1 and weak_enemy_2); choose both.
    assert game._pending_card_action_choice is not None
    assert game._pending_card_action_choice.min_choices == 0
    game.resolve_pending_card_action([0, 1])

    assert harpy_mother in player.discard_pile
    assert weak_enemy_1 in player.cards_laid_out
    assert weak_enemy_2 in player.cards_laid_out
    assert strong_enemy in opponent.cards_laid_out


def test_defending_harpy_mother_lets_owner_choose_weak_enemy_creatures_to_take() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    strong_attacker = Luchataur()
    weak_enemy_1 = Chameleon_sniper()
    weak_enemy_2 = Tiger_squirrel()
    strong_enemy = Luchataur()
    harpy_mother = Harpy_mother()

    attacker_owner.cards_laid_out = [
        strong_attacker,
        weak_enemy_1,
        weak_enemy_2,
        strong_enemy,
    ]
    defender_owner.cards_laid_out = [harpy_mother]
    attacker_owner.hand = [Shield_bugs()]
    defender_owner.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_card_action_choice is not None
    assert game._pending_card_action_choice.action_key == "harpy_mother"
    assert game._pending_card_action_choice.responding_player_index == game.players.index(
        defender_owner
    )
    assert game._pending_card_action_choice.selection_owner_index == game.players.index(
        attacker_owner
    )
    assert game._pending_card_action_choice.eligible_indices == [1, 2]
    assert game._pending_card_action_choice.min_choices == 0
    assert game._pending_card_action_choice.max_choices == 2
    assert game._pending_combat_finalization is not None

    game.resolve_pending_card_action([1, 2])

    assert weak_enemy_1 in defender_owner.cards_laid_out
    assert weak_enemy_2 in defender_owner.cards_laid_out
    assert strong_attacker in attacker_owner.cards_laid_out
    assert strong_enemy in attacker_owner.cards_laid_out
    assert harpy_mother in defender_owner.discard_pile
    assert game._pending_combat_finalization is None


def test_defending_harpy_mother_can_decline_only_eligible_weak_enemy_creature() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    strong_attacker = Luchataur()
    weak_enemy = Tiger_squirrel()
    strong_enemy = Luchataur()
    harpy_mother = Harpy_mother()

    attacker_owner.cards_laid_out = [strong_attacker, weak_enemy, strong_enemy]
    defender_owner.cards_laid_out = [harpy_mother]
    attacker_owner.hand = [Shield_bugs()]
    defender_owner.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_card_action_choice is not None
    assert game._pending_card_action_choice.action_key == "harpy_mother"
    assert game._pending_card_action_choice.eligible_indices == [1]
    assert game._pending_card_action_choice.min_choices == 0
    assert game._pending_card_action_choice.max_choices == 1
    assert game._pending_combat_finalization is not None

    game.resolve_pending_card_action([])

    assert weak_enemy in attacker_owner.cards_laid_out
    assert strong_attacker in attacker_owner.cards_laid_out
    assert strong_enemy in attacker_owner.cards_laid_out
    assert harpy_mother in defender_owner.discard_pile
    assert game._pending_combat_finalization is None


def test_defeated_strange_barrel_steals_up_to_2_cards_from_opponent_hand() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    strange_barrel = Strange_barrel()
    enemy_creature = Luchataur()
    opponent_card_1 = Chameleon_sniper()
    opponent_card_2 = Tiger_squirrel()

    player.cards_laid_out = [strange_barrel]
    player.hand = []
    opponent.cards_laid_out = [enemy_creature]
    opponent.hand = [opponent_card_1, opponent_card_2]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert strange_barrel in player.discard_pile
    assert len(player.hand) == 2
    assert opponent_card_1 in player.hand
    assert opponent_card_2 in player.hand
    assert opponent.hand == []


def test_defeated_action_draws_up_to_five_cards_for_any_player_below_five_cards() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    strange_barrel = Strange_barrel()
    enemy_creature = Luchataur()
    replacement_cards = [Shield_bugs(), Luchataur(), Explosive_toad()]
    opponent_card_1 = Chameleon_sniper()
    opponent_card_2 = Tiger_squirrel()
    opponent_card_3 = Ferret_bomber()
    opponent_card_4 = Explosive_toad()

    player.cards_laid_out = [strange_barrel]
    opponent.cards_laid_out = [enemy_creature]
    opponent.hand = [opponent_card_1, opponent_card_2, opponent_card_3, opponent_card_4]
    opponent.draw_pile = DrawPile(replacement_cards.copy())

    with patch("cards.randint", side_effect=[0, 0]):
        _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert len(opponent.hand) == 5
    assert all(card in opponent.hand for card in replacement_cards)
    

def test_defeated_harpy_mother_takes_control_of_2_tough_enemy_creatures_without_changing_tough_charges() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    harpy_mother = Harpy_mother()
    tough_enemy_with_zero = Shield_bugs()
    tough_enemy_with_zero.tough_charges = 0
    tough_enemy_with_one = Plated_scorpion()
    strong_enemy = Luchataur()

    player.cards_laid_out = [harpy_mother]
    player.hand = [Chameleon_sniper()]  # Keep game active while choice is pending.
    opponent.cards_laid_out = [tough_enemy_with_zero, tough_enemy_with_one, strong_enemy]

    _attack_and_defend(game, attacker_index=0, defender_index=2)
    # Eligible indices are [0, 1] (tough_enemy_with_zero and tough_enemy_with_one); choose both.
    game.resolve_pending_card_action([0, 1])

    assert harpy_mother in player.discard_pile
    assert tough_enemy_with_zero in player.cards_laid_out
    assert tough_enemy_with_one in player.cards_laid_out
    assert tough_enemy_with_zero.tough_charges == 0
    assert tough_enemy_with_one.tough_charges == 1
    assert tough_enemy_with_zero not in opponent.cards_laid_out
    assert tough_enemy_with_one not in opponent.cards_laid_out


def test_snail_hydra_attacks_and_by_action_attack_destroys_explosive_toad_and_explosive_toad_defeated_action_destroys_attacking_snail_hydra_thus_attack_is_cancelled_and_turn_has_ended() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    snail_hydra = Snail_hydra()
    explosive_toad = Explosive_toad()
    weak_enemy = Ferret_bomber()

    player.cards_laid_out = [snail_hydra]
    # Keep the game active after Snail Hydra is destroyed.
    player.hand = [Tiger_squirrel()]
    # 1 < 2 so Snail Hydra ATTACK action is active.
    opponent.cards_laid_out = [weak_enemy, explosive_toad]

    game.attack(attacker_index=0)
    # Snail Hydra's ATTACK action: eligible [0, 1]; select explosive_toad (index 1).
    # Explosive Toad's DEFEATED action auto-selects Snail Hydra (only target), cancelling the pending attack.
    game.resolve_pending_card_action([1])

    assert snail_hydra in player.discard_pile
    assert explosive_toad in opponent.discard_pile
    assert snail_hydra not in player.cards_laid_out
    assert explosive_toad not in opponent.cards_laid_out
    # NOTE - making sure attack was cancelled and weak_enemy was not destroyed.
    assert weak_enemy in opponent.cards_laid_out
    assert weak_enemy not in opponent.discard_pile
    assert game.game_state == GameState.ACTIVE


# ── DEFEATED ordering tests ──────────────────────────────────────────────


def test_two_defeated_actions_equal_strength_creates_ordering() -> None:
    """When both creatures have DEFEATED actions, equal strength, and both die,
    a pending ordering prompt is created."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    attacker_toad = Explosive_toad()  # strength 5, DEFEATED
    defender_harpy = Harpy_mother()  # strength 5, DEFEATED

    player.cards_laid_out = [attacker_toad]
    opponent.cards_laid_out = [defender_harpy]
    # Keep game active
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    # Both die (equal strength 5)
    assert game._pending_defeated_ordering is not None
    assert len(game._pending_defeated_ordering.entries) == 2
    assert attacker_toad in player.discard_pile
    assert defender_harpy in opponent.discard_pile
    # Attack is NOT finalized yet - waiting for ordering
    assert game._pending_combat_finalization is not None


def test_defeated_ordering_triggers_actions_in_chosen_order() -> None:
    """Player chooses order [1, 0] — the second entry (defender) triggers first."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    attacker_toad = Explosive_toad()  # strength 5, DEFEATED: defeat a creature of choice
    defender_harpy = Harpy_mother()  # strength 5, DEFEATED: take control of weak enemies

    extra_enemy = Chameleon_sniper()  # strength 1, on opponent side (target for toad)
    player.cards_laid_out = [attacker_toad]
    opponent.cards_laid_out = [defender_harpy, extra_enemy]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_defeated_ordering is not None

    # Choose order: [1, 0] means defender_harpy's DEFEATED fires first
    # Harpy Mother: take control of enemy creatures with power <= 5
    # But Harpy Mother belongs to opponent, and game.current_player is the attacker.
    # So harpy's trigger_defeated_effect uses game.opponent's cards (attacker's creatures)
    # Attacker has no creatures left (toad was destroyed), so harpy has nothing to take.
    # Then Explosive Toad fires: defeat a creature of choice from opponent's side.
    # extra_enemy is still on opponent's battlefield.
    game.resolve_pending_defeated_ordering([1, 0])

    # Toad's DEFEATED action targets extra_enemy (auto-selected since it's the only one)
    assert extra_enemy in opponent.discard_pile


def test_defeated_ordering_with_pending_card_action_choice() -> None:
    """When first DEFEATED action creates a pending choice, the second waits."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    # Use different DEFEATED card types (same strength 5) to avoid dataclass
    # equality confusion in owner lookup.
    attacker_toad = Explosive_toad()  # strength 5, DEFEATED: choose creature to defeat
    defender_harpy = Harpy_mother()  # strength 5, DEFEATED: take control of weak enemies

    player_extra = Luchataur()
    opponent_extra_1 = Ferret_bomber()
    opponent_extra_2 = Chameleon_sniper()

    player.cards_laid_out = [attacker_toad, player_extra]
    opponent.cards_laid_out = [defender_harpy, opponent_extra_1, opponent_extra_2]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_defeated_ordering is not None
    assert len(game._pending_defeated_ordering.entries) == 2

    # Choose order: attacker toad first [0], then defender harpy [1]
    game.resolve_pending_defeated_ordering([0, 1])

    # Attacker toad's DEFEATED: targets opponent's creatures.
    # opponent has [opponent_extra_1, opponent_extra_2] (defender_harpy already in discard).
    # 2 eligible targets → pending choice
    assert game._pending_card_action_choice is not None
    game.resolve_pending_card_action([0])  # destroy opponent_extra_1

    assert opponent_extra_1 in opponent.discard_pile


def test_defeated_ordering_only_one_survives_tough_no_ordering_prompt() -> None:
    """When one creature has TOUGH and survives the initial combat, no ordering
    prompt appears — the single deferred DEFEATED action triggers immediately."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    explosive_toad = Explosive_toad()  # strength 5, DEFEATED
    knightmare = Knightmare()  # strength 5, TOUGH, DEFEATED

    player.cards_laid_out = [explosive_toad]
    opponent.cards_laid_out = [knightmare]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    # Both have equal strength, but Knightmare has TOUGH (1 charge) → survives initial combat
    # No ordering prompt since only 1 DEFEATED actually fires
    assert game._pending_defeated_ordering is None
    assert explosive_toad in player.discard_pile  # destroyed, DEFEATED triggers immediately


def test_defeated_ordering_validation_rejects_wrong_count() -> None:
    """Ordering with wrong number of indices raises ValueError."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    toad1 = Explosive_toad()
    toad2 = Explosive_toad()

    player.cards_laid_out = [toad1]
    opponent.cards_laid_out = [toad2]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_defeated_ordering is not None

    try:
        game.resolve_pending_defeated_ordering([0])  # only 1 index for 2 entries
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_defeated_ordering_validation_rejects_invalid_indices() -> None:
    """Ordering with duplicate or out-of-range indices raises ValueError."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    toad1 = Explosive_toad()
    toad2 = Explosive_toad()

    player.cards_laid_out = [toad1]
    opponent.cards_laid_out = [toad2]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_defeated_ordering is not None

    try:
        game.resolve_pending_defeated_ordering([0, 0])  # duplicate
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_defeated_ordering_game_over_during_queue_stops_processing() -> None:
    """If game ends during DEFEATED queue processing, remaining actions are skipped."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    # Knightmare's DEFEATED: "You lose the game"
    # Explosive Toad's DEFEATED: "Defeat a creature of your choice"
    knightmare = Knightmare()
    knightmare.tough_charges = 0  # disable TOUGH so it actually dies
    explosive_toad = Explosive_toad()

    player.cards_laid_out = [knightmare]
    opponent.cards_laid_out = [explosive_toad]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game._pending_defeated_ordering is not None

    # Trigger Knightmare first → game over (player loses)
    game.resolve_pending_defeated_ordering([0, 1])

    assert game.game_state == GameState.GAME_OVER
    assert game.winner == opponent
    # Queue should be cleared
    assert game._defeated_action_queue == []


def test_attacker_defeated_action_destroys_defender_no_crash() -> None:
    """When attacker's DEFEATED action destroys the defender (who was also
    defeated in combat), _resolve_combat should not crash with list.remove."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    # Explosive Toad (strength 5, DEFEATED: defeat a creature of choice)
    # attacks a plain strength-5 creature without DEFEATED.
    # Both die (equal strength). Toad's DEFEATED fires immediately and
    # auto-selects the defender as its target (only enemy creature).
    # Then _resolve_combat tries to destroy the defender again — should not crash.
    toad = Explosive_toad()
    plain_defender = Card(name="Plain Fighter", strength=5)

    player.cards_laid_out = [toad]
    opponent.cards_laid_out = [plain_defender]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    # This should not raise "list.remove(x): x not in list"
    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert toad in player.discard_pile
    assert plain_defender in opponent.discard_pile


def test_harpy_mother_defeated_auto_ends_turn() -> None:
    """After Harpy Mother's DEFEATED effect resolves (takes control of creatures),
    the turn should auto-end when auto_end_turn_after_resolved_attack is enabled."""
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        enforce_turn_action_limit=True,
        auto_end_turn_after_resolved_attack=True,
    )
    game.start_game()
    # Force Player 1 to go first
    game.turn = 0
    player = game.players[0]
    opponent = game.players[1]

    harpy_mother = Harpy_mother()
    # Use a non-FRENZY attacker so turn auto-ends after combat
    strong_attacker = Card(name="Strong Attacker", strength=9)
    weak_creature = Chameleon_sniper()  # strength 1, eligible for Harpy Mother

    opponent.cards_laid_out = [harpy_mother, weak_creature]
    player.cards_laid_out = [strong_attacker]
    player.hand = [Tiger_squirrel()]
    opponent.hand = [Chameleon_sniper()]

    # Attack Harpy Mother (strength 5) with Strong Attacker (strength 9) — Harpy Mother dies
    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    # Harpy Mother's DEFEATED: take control of weak creatures (auto-selects weak_creature)
    # After resolution, turn should auto-end
    assert harpy_mother in opponent.discard_pile
    assert weak_creature in opponent.cards_laid_out  # Harpy Mother takes it for opponent
    assert game.current_player.name == "Player 2"  # turn passed to opponent
