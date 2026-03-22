from base_classes import Game
from cards import Gorillion, Shield_bugs, Luchataur


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


# Destroying TOUGH creatures
def test_destroy_tough_creature_with_one_charge_survives_and_loses_charge() -> None:
    game = _new_game()
    owner = game.current_player
    tough_creature = Shield_bugs()
    owner.cards_laid_out = [tough_creature]

    game._destroy_creature(owner, tough_creature)

    assert tough_creature in owner.cards_laid_out
    assert tough_creature.tough_charges == 0
    assert tough_creature not in owner.discard_pile


def test_destroy_tough_creature_with_zero_charges_moves_to_discard() -> None:
    game = _new_game()
    owner = game.current_player
    tough_creature = Shield_bugs()
    tough_creature.tough_charges = 0
    owner.cards_laid_out = [tough_creature]

    game._destroy_creature(owner, tough_creature)

    assert tough_creature not in owner.cards_laid_out
    assert tough_creature in owner.discard_pile


def test_destroy_tough_creature_with_ignore_tough_true_moves_to_discard() -> None:
    game = _new_game()
    owner = game.current_player
    tough_creature = Shield_bugs()
    owner.cards_laid_out = [tough_creature]

    game._destroy_creature(owner, tough_creature, ignore_tough=True)

    assert tough_creature not in owner.cards_laid_out
    assert tough_creature in owner.discard_pile
    assert tough_creature.tough_charges == 1


# Attacks against TOUGH creatures
def test_attack_defeated_tough_creature_with_one_charge_survives_and_loses_charge() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent
    attacker = Gorillion()
    tough_creature = Shield_bugs()
    attacker_owner.cards_laid_out = [attacker]
    defender_owner.cards_laid_out = [tough_creature]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert tough_creature in defender_owner.cards_laid_out
    assert tough_creature.tough_charges == 0
    assert tough_creature not in defender_owner.discard_pile


def test_attack_defeated_tough_creature_with_zero_charges_moves_to_discard() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent
    attacker = Gorillion()
    tough_creature = Shield_bugs()
    tough_creature.tough_charges = 0
    attacker_owner.cards_laid_out = [attacker]
    defender_owner.cards_laid_out = [tough_creature]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert tough_creature not in defender_owner.cards_laid_out
    assert tough_creature in defender_owner.discard_pile


def test_attack_tough_creature_twice_first_consumes_tough_then_moves_to_discard() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent
    attacker = Luchataur()
    tough_creature = Shield_bugs()
    attacker_owner.cards_laid_out = [attacker]
    defender_owner.cards_laid_out = [tough_creature]

    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert tough_creature in defender_owner.cards_laid_out
    assert tough_creature.tough_charges == 0
    assert attacker in attacker_owner.cards_laid_out

    # FRENZY: attacker chooses to attack again in the same turn.
    _attack_and_defend(game, attacker_index=0, defender_index=0)

    assert tough_creature not in defender_owner.cards_laid_out
    assert tough_creature in defender_owner.discard_pile
    assert attacker in attacker_owner.cards_laid_out
