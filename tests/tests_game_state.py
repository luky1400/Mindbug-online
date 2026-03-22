import pytest

from base_classes import Game
from cards import Luchataur, Tiger_squirrel, get_card_pool
from enums import CardSet, GameState


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )
    game.start_game(card_pool=[])
    return game


def test_initial_game_state_is_start_turn_before_start_game() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )

    assert game.game_state == GameState.START_TURN
    assert game.winner is None


def test_start_game_sets_state_to_active_and_resets_winner() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )
    game.winner = game.players[0]

    game.start_game(card_pool=[])

    assert game.game_state == GameState.ACTIVE
    assert game.turn in (0, 1)
    assert game.current_player in game.players
    assert game.winner is None


def test_end_turn_switches_player_and_sets_start_turn_state() -> None:
    game = _new_game()
    first_player = game.current_player

    game.end_turn()

    assert game.game_state == GameState.START_TURN
    assert game.current_player is not first_player


def test_attack_that_reduces_opponent_to_zero_life_sets_game_over_and_winner() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    player.cards_laid_out = [Luchataur()]
    opponent.number_of_lives = 1

    game.attack(attacker_index=0, defender_index=None)

    assert opponent.number_of_lives == 0
    assert game.game_state == GameState.GAME_OVER
    assert game.winner is player


def test_actions_raise_error_after_game_is_over() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    player.cards_laid_out = [Luchataur()]
    opponent.number_of_lives = 1
    game.attack(attacker_index=0, defender_index=None)

    with pytest.raises(ValueError, match="Game is already over."):
        game.end_turn()

    with pytest.raises(ValueError, match="Game is already over."):
        game.play_card(hand_index=0, card=Tiger_squirrel())


def test_start_game_uses_only_selected_card_sets() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=5,
        starting_draw_pile_size=5,
    )

    game.start_game(card_pool=get_card_pool(), sets=[CardSet.FIRST_CONTACT])

    assert game.selected_sets == [CardSet.FIRST_CONTACT]

    for player in game.players:
        assert all(card.set == CardSet.FIRST_CONTACT for card in player.hand)
        assert all(card.set == CardSet.FIRST_CONTACT for card in player.draw_pile.cards)


def test_start_game_stores_all_available_sets_when_no_filter_is_passed() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )

    game.start_game(card_pool=get_card_pool())

    assert game.selected_sets == [
        CardSet.FIRST_CONTACT,
        CardSet.NEW_SERVANTS,
        CardSet.PROMO_CARDS,
    ]
