import pytest

from base_classes import Game
from cards import Brain_fly, Luchataur, Tiger_squirrel


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
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
