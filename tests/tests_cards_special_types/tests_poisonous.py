from base_classes import Game
from cards import Axolotl_healer, Gorillion, Shield_bugs


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
    )
    game.start_game(card_pool=[])
    return game


def test_poisonous_attacker_defeats_stronger_non_tough_defender() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    poisonous_attacker = Axolotl_healer()  # POISONOUS, strength 4
    strong_defender = Gorillion()  # strength 10

    attacker_owner.cards_laid_out = [poisonous_attacker]
    defender_owner.cards_laid_out = [strong_defender]

    game.attack(attacker_index=0, defender_index=0)

    # Defender is defeated due to POISONOUS, regardless of power.
    assert strong_defender in defender_owner.discard_pile
    assert strong_defender not in defender_owner.cards_laid_out
    # Attacker is also defeated by normal strength comparison (10 >= 4).
    assert poisonous_attacker in attacker_owner.discard_pile
    assert poisonous_attacker not in attacker_owner.cards_laid_out


def test_poisonous_defender_defeats_stronger_attacker_when_blocking() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    strong_attacker = Gorillion()  # strength 10
    poisonous_defender = Axolotl_healer()  # POISONOUS, strength 4

    attacker_owner.cards_laid_out = [strong_attacker]
    defender_owner.cards_laid_out = [poisonous_defender]

    game.attack(attacker_index=0, defender_index=0)

    # Attacker is defeated because blocker is POISONOUS.
    assert strong_attacker in attacker_owner.discard_pile
    assert strong_attacker not in attacker_owner.cards_laid_out
    # Blocker is also defeated by normal strength comparison.
    assert poisonous_defender in defender_owner.discard_pile
    assert poisonous_defender not in defender_owner.cards_laid_out


def test_poisonous_damage_consumes_tough_then_next_hit_defeats_creature() -> None:
    game = _new_game()
    attacker_owner = game.current_player
    defender_owner = game.opponent

    poisonous_attacker = Axolotl_healer()  # POISONOUS, strength 4
    tough_defender = Shield_bugs()  # TOUGH, starts with tough_charges=1

    attacker_owner.cards_laid_out = [poisonous_attacker]
    # Keep the game active after first combat even if the attacker is defeated.
    attacker_owner.hand = [Gorillion()]
    defender_owner.cards_laid_out = [tough_defender]

    # First hit: defender survives due to TOUGH and spends a charge.
    game.attack(attacker_index=0, defender_index=0)
    assert tough_defender in defender_owner.cards_laid_out
    assert tough_defender.tough_charges == 0
    assert tough_defender not in defender_owner.discard_pile

    # Rebuild attacker board for a second poisonous attack.
    attacker_owner.cards_laid_out = [Axolotl_healer()]
    game.attack(attacker_index=0, defender_index=0)

    assert tough_defender not in defender_owner.cards_laid_out
    assert tough_defender in defender_owner.discard_pile
