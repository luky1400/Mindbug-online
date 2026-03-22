from base_classes import DrawPile, Game
from unittest.mock import patch
from cards import (
    Chameleon_sniper,
    Explosive_toad,
    Ferret_bomber,
    Harpy_mother,
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
    game.start_game(card_pool=[])
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

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert explosive_toad in player.discard_pile
    assert explosive_toad not in player.cards_laid_out
    assert enemy_creature in opponent.discard_pile
    assert enemy_creature not in opponent.cards_laid_out


def test_defeated_harpy_mother_takes_control_of_up_to_2_weak_enemy_creatures() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    harpy_mother = Harpy_mother()
    weak_enemy_1 = Chameleon_sniper()
    weak_enemy_2 = Ferret_bomber()
    strong_enemy = Luchataur()

    player.cards_laid_out = [harpy_mother]
    opponent.cards_laid_out = [weak_enemy_1, weak_enemy_2, strong_enemy]

    _attack_and_defend(game, attacker_index=0, defender_index=2)

    assert harpy_mother in player.discard_pile
    assert weak_enemy_1 in player.cards_laid_out
    assert weak_enemy_2 in player.cards_laid_out
    assert strong_enemy in opponent.cards_laid_out


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
    opponent.cards_laid_out = [tough_enemy_with_zero, tough_enemy_with_one, strong_enemy]

    _attack_and_defend(game, attacker_index=0, defender_index=2)

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

    # First random pick: Snail Hydra ATTACK action destroys Explosive Toad (index 1).
    # Second random pick: Explosive Toad DEFEATED action destroys Snail Hydra (index 0).
    with patch("cards.randint", side_effect=[1, 0]):
        game.attack(attacker_index=0)

    assert snail_hydra in player.discard_pile
    assert explosive_toad in opponent.discard_pile
    assert snail_hydra not in player.cards_laid_out
    assert explosive_toad not in opponent.cards_laid_out
    # NOTE - making sure attack was cancelled and weak_enemy was not destroyed.
    assert weak_enemy in opponent.cards_laid_out
    assert weak_enemy not in opponent.discard_pile
    assert game.game_state == GameState.ACTIVE
