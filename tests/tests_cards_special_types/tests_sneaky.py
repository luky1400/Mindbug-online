import pytest

from base_classes import Game
from cards import Chameleon_sniper, Luchataur, Tiger_squirrel


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )
    game.start_game(card_pool=[])
    return game


def test_sneaky_attacker_cannot_be_blocked_by_non_sneaky_defender() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    sneaky_attacker = Chameleon_sniper()
    non_sneaky_defender = Luchataur()
    player.cards_laid_out = [sneaky_attacker]
    opponent.cards_laid_out = [non_sneaky_defender]

    with pytest.raises(ValueError, match="only SNEAKY creatures can defend against SNEAKY attackers"):
        game.attack(attacker_index=0, defender_index=0)


def test_sneaky_attacker_can_be_blocked_by_sneaky_defender() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    sneaky_attacker = Chameleon_sniper()
    sneaky_defender = Tiger_squirrel()
    player.cards_laid_out = [sneaky_attacker]
    opponent.cards_laid_out = [sneaky_defender]

    game.attack(attacker_index=0, defender_index=0)

    assert sneaky_attacker in player.discard_pile
    assert sneaky_attacker not in player.cards_laid_out
    assert sneaky_defender in opponent.cards_laid_out
