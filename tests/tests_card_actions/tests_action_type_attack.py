from base_classes import DrawPile, Game
from cards import (
    Brain_fly,
    Chameleon_sniper,
    Count_draculeech,
    Ferret_bomber,
    Luchataur,
    Majestic_manticore,
    Shark_dog,
    Shield_bugs,
    Short_neck_giraffodile,
    Snail_hydra,
    The_lurker,
    Tiger_squirrel,
    Turbo_bug,
    Turf_the_surfer,
    Tusked_extorter,
)
from enums import CardSpecialType, GameState


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


def test_attack_majestic_manticore_defeats_all_lowest_power_creatures() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    lowest_1 = Chameleon_sniper()  # 1
    lowest_2 = Chameleon_sniper()  # 1
    non_lowest_1 = Ferret_bomber()  # 2
    non_lowest_2 = Brain_fly()  # 4

    player.cards_laid_out = [Majestic_manticore()]
    opponent.cards_laid_out = [non_lowest_1, lowest_1, lowest_2, non_lowest_2]

    # Attack a non-lowest creature so combat does not affect the expectation.
    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert lowest_1 in opponent.discard_pile
    assert lowest_2 in opponent.discard_pile
    assert lowest_1 not in opponent.cards_laid_out
    assert lowest_2 not in opponent.cards_laid_out


def test_attack_short_neck_giraffodile_draws_2_cards_from_discard_pile() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    discard_card_1 = Chameleon_sniper()
    discard_card_2 = Tiger_squirrel()

    player.cards_laid_out = [Short_neck_giraffodile()]
    player.discard_pile = [discard_card_1, discard_card_2]
    player.hand = []

    opponent.cards_laid_out = [Brain_fly()]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert player.discard_pile == []
    assert discard_card_1 in player.hand
    assert discard_card_2 in player.hand
    assert len(player.hand) == 2


def test_attack_tusked_extorter_opponent_discards_a_card_from_hand() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    card_to_discard = Chameleon_sniper()
    opponent.hand = [card_to_discard]
    opponent.discard_pile = []

    player.cards_laid_out = [Tusked_extorter()]
    opponent.cards_laid_out = [Luchataur()]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert opponent.hand == []
    assert card_to_discard in opponent.discard_pile


def test_attack_chameleon_sniper_opponent_loses_1_life() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    opponent.number_of_lives = 5
    player.cards_laid_out = [Chameleon_sniper()]
    opponent.cards_laid_out = [Tiger_squirrel()]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert opponent.number_of_lives == 4


def test_attack_turbo_bug_sets_opponent_life_to_1() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    opponent.number_of_lives = 5
    # Keep game active even if attacker is defeated in combat.
    player.hand = [Tiger_squirrel()]
    player.cards_laid_out = [Turbo_bug()]
    opponent.cards_laid_out = [Luchataur()]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert opponent.number_of_lives == 1


def test_attack_count_draculeech_loses_1_life_and_defeats_an_enemy_creature() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    weak_enemy = Ferret_bomber()
    target_enemy = Luchataur()
    player.number_of_lives = 5
    player.cards_laid_out = [Count_draculeech()]
    opponent.cards_laid_out = [weak_enemy, target_enemy]

    game.attack(attacker_index=0)
    game.resolve_pending_card_action([1])
    game.defend(defender_index=0)

    assert player.number_of_lives == 4
    assert target_enemy in opponent.discard_pile
    assert target_enemy not in opponent.cards_laid_out


def test_attack_action_draws_up_to_five_cards_if_owner_hand_is_below_five() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent
    replacement_cards = [Tiger_squirrel(), Brain_fly(), Ferret_bomber()]

    player.hand = [Shield_bugs(), Luchataur()]
    player.draw_pile = DrawPile(replacement_cards.copy())
    player.cards_laid_out = [Chameleon_sniper()]
    opponent.cards_laid_out = [Tiger_squirrel()]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert len(player.hand) == 5
    assert all(card in player.hand for card in replacement_cards)


def test_attack_shark_dog_defeats_enemy_with_power_6_or_more() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    weak_enemy = Ferret_bomber()
    strong_enemy_1 = Luchataur()
    strong_enemy_2 = Majestic_manticore()
    player.cards_laid_out = [Shark_dog()]
    opponent.cards_laid_out = [weak_enemy, strong_enemy_1, strong_enemy_2]

    # Eligible indices are [1, 2] (strong_enemy_1 and strong_enemy_2); choose index 2 (strong_enemy_2).
    game.attack(attacker_index=0)
    game.resolve_pending_card_action([2])
    game.defend(defender_index=0)

    assert strong_enemy_2 in opponent.discard_pile
    assert strong_enemy_2 not in opponent.cards_laid_out


def test_attack_turf_the_surfer_sets_selected_enemy_cannot_block() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    defender = Shield_bugs()
    selected_enemy = Luchataur()
    player.cards_laid_out = [Turf_the_surfer()]
    opponent.cards_laid_out = [defender, selected_enemy]

    game.attack(attacker_index=0)
    game.resolve_pending_card_action([1])
    game.defend(defender_index=0)

    assert selected_enemy.cannot_block is True


def test_attack_the_lurker_gains_sneaky_when_owner_controls_more_creatures() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    lurker = The_lurker()
    ally = Ferret_bomber()
    player.cards_laid_out = [lurker, ally]
    opponent.cards_laid_out = [Luchataur()]
    # Keep game active after direct attack.
    opponent.hand = [Tiger_squirrel()]

    game.attack(attacker_index=0)

    assert CardSpecialType.SNEAKY in lurker.special_types


def test_shark_dog_attack_action_choice_resolves_without_error_when_pending_defense_also_exists() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        auto_end_turn_after_resolved_attack=True,
    )
    game.start_game()
    player = game.current_player
    opponent = game.opponent

    strong_enemy_1 = Luchataur()
    strong_enemy_2 = Majestic_manticore()
    player.cards_laid_out = [Shark_dog()]
    # Two strong enemies (both ≥6) so auto-selection is not triggered.
    opponent.cards_laid_out = [strong_enemy_1, strong_enemy_2]

    # Shark Dog ATTACK action creates a pending choice AND a pending defense simultaneously.
    # With auto_end_turn_after_resolved_attack=True, resolving the choice used to call
    # end_turn() while _pending_defense_decision was still set, raising a ValueError.
    game.attack(attacker_index=0)
    game.resolve_pending_card_action([0])  # destroy strong_enemy_1

    # Pending defense should still be set (not auto-ended).
    assert game._pending_defense_decision is not None
    assert strong_enemy_1 in opponent.discard_pile
    game.defend(defender_index=None)  # direct attack


def test_shark_dog_hunter_attack_triggers_action_before_combat() -> None:
    """Shark Dog (HUNTER + ATTACK action) targeting a defender should trigger its
    ATTACK action before combat. The targeted defender should still be alive when
    the action resolves, and combat happens after."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    shark_dog = Shark_dog()
    strong_enemy = Luchataur()  # strength 9, eligible for Shark Dog action
    weak_enemy = Ferret_bomber()  # strength 2, not eligible
    player.cards_laid_out = [shark_dog]
    opponent.cards_laid_out = [weak_enemy, strong_enemy]

    # Shark Dog attacks targeting strong_enemy (index 1) via HUNTER.
    # ATTACK action fires first — only strong_enemy is eligible (>=6).
    # Auto-resolved: destroys strong_enemy before combat.
    game.attack(attacker_index=0, defender_index=1)

    # strong_enemy was the HUNTER target AND the only eligible action target.
    # Action auto-resolves (1 eligible = auto-select), destroying strong_enemy.
    # Since the HUNTER target was destroyed, combat is cancelled.
    assert strong_enemy in opponent.discard_pile
    assert strong_enemy not in opponent.cards_laid_out
    assert shark_dog in player.cards_laid_out  # Shark Dog survives (no combat)


def test_shark_dog_hunter_attack_action_pending_then_destroys_target() -> None:
    """When Shark Dog HUNTER targets a defender and the ATTACK action requires a
    choice (multiple eligible), destroying the HUNTER target via the action should
    cancel combat."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    shark_dog = Shark_dog()
    hunter_target = Luchataur()  # strength 9
    other_strong = Majestic_manticore()  # strength 6
    player.cards_laid_out = [shark_dog]
    opponent.cards_laid_out = [hunter_target, other_strong]

    # HUNTER targets hunter_target (index 0).
    # ATTACK action has 2 eligible targets (both >=6), so pending choice is created.
    game.attack(attacker_index=0, defender_index=0)
    assert game._pending_card_action_choice is not None
    assert game._pending_attack_continuation is not None

    # Player chooses to destroy hunter_target (index 0) via the action.
    game.resolve_pending_card_action([0])

    # hunter_target was the HUNTER target and was destroyed by action — combat cancelled.
    assert hunter_target in opponent.discard_pile
    assert shark_dog in player.cards_laid_out  # Shark Dog survives


def test_shark_dog_hunter_attack_action_pending_then_target_survives() -> None:
    """When Shark Dog HUNTER targets a defender and the ATTACK action destroys a
    different creature, combat should proceed normally against the HUNTER target."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    shark_dog = Shark_dog()  # strength 4
    hunter_target = Luchataur()  # strength 9
    other_strong = Majestic_manticore()  # strength 6
    player.cards_laid_out = [shark_dog]
    opponent.cards_laid_out = [hunter_target, other_strong]

    # HUNTER targets hunter_target (index 0). Pending choice created.
    game.attack(attacker_index=0, defender_index=0)

    # Player chooses to destroy other_strong (index 1) instead.
    game.resolve_pending_card_action([1])

    # hunter_target survived the action, so combat resolves.
    # Shark Dog (4) vs Luchataur (9) — Shark Dog is defeated.
    assert other_strong in opponent.discard_pile
    assert shark_dog in player.discard_pile  # lost combat
    assert hunter_target in opponent.cards_laid_out  # won combat


def test_shark_dog_hunter_no_eligible_action_targets_still_resolves_combat() -> None:
    """Shark Dog HUNTER targeting a weak defender (no eligible action targets)
    should still resolve combat normally."""
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    shark_dog = Shark_dog()  # strength 4
    weak_enemy = Ferret_bomber()  # strength 2, not eligible for action
    player.cards_laid_out = [shark_dog]
    opponent.cards_laid_out = [weak_enemy]

    # HUNTER targets weak_enemy. No action targets (none >=6), action is a no-op.
    # Combat resolves: Shark Dog (4) vs Ferret Bomber (2) — Ferret Bomber defeated.
    game.attack(attacker_index=0, defender_index=0)

    assert weak_enemy in opponent.discard_pile
    assert shark_dog in player.cards_laid_out