import pytest

from base_classes import Game
from cards import Brain_fly, Luchataur, Tiger_squirrel


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
    )
    game.start_game(card_pool=[])
    return game


def _attack_and_defend(game: Game, attacker_index: int = 0, defender_index: int | None = 0) -> None:
    game.attack(attacker_index=attacker_index)
    game.defend(defender_index=defender_index)


def test_non_frenzy_creature_can_attack_only_once_per_turn() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    attacker = Brain_fly()  # non-FRENZY
    blocker_1 = Tiger_squirrel()
    blocker_2 = Tiger_squirrel()
    player.cards_laid_out = [attacker]
    # Keep game active after attacker is defeated in first combat.
    player.hand = [Tiger_squirrel()]
    opponent.cards_laid_out = [blocker_1, blocker_2]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    with pytest.raises(ValueError, match="cannot attack more than 1 times this turn"):
        game.attack(attacker_index=0)


def test_frenzy_creature_can_attack_twice_but_not_three_times_per_turn() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    attacker = Luchataur()  # FRENZY
    blocker_1 = Tiger_squirrel()
    blocker_2 = Tiger_squirrel()
    blocker_3 = Tiger_squirrel()
    player.cards_laid_out = [attacker]
    opponent.cards_laid_out = [blocker_1, blocker_2, blocker_3]

    _attack_and_defend(game, attacker_index=0, defender_index=0)
    _attack_and_defend(game, attacker_index=0, defender_index=0)

    with pytest.raises(ValueError, match="cannot attack more than 2 times this turn"):
        game.attack(attacker_index=0)


def test_multiplayer_attack_automatically_passes_turn_when_not_frenzy_bonus_case() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        enforce_turn_action_limit=True,
        auto_end_turn_after_resolved_attack=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent
    player.cards_laid_out = [Brain_fly()]
    player.hand = [Tiger_squirrel()]
    opponent.cards_laid_out = [Tiger_squirrel()]
    opponent.hand = [Tiger_squirrel()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game.current_player is opponent


def test_multiplayer_frenzy_survivor_keeps_turn_for_optional_second_attack() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        enforce_turn_action_limit=True,
        auto_end_turn_after_resolved_attack=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent
    frenzy_attacker = Luchataur()
    weak_blocker = Tiger_squirrel()
    player.cards_laid_out = [frenzy_attacker]
    opponent.cards_laid_out = [weak_blocker]
    opponent.hand = [Tiger_squirrel()]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert game.current_player is player
    assert game._pending_frenzy_attacker_id == id(frenzy_attacker)
    assert game.can_end_turn_manually() is True


def test_manual_end_turn_is_not_available_without_pending_frenzy_attack() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        enforce_turn_action_limit=True,
        auto_end_turn_after_resolved_attack=True,
    )
    game.start_game(card_pool=[])

    assert game.can_end_turn_manually() is False
