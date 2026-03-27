from base_classes import Game
from cards import (
    Bugserker,
    Chameleon_sniper,
    Deathweaver,
    Ferret_bomber,
    Ferret_pacifier,
    Froblin_instigator,
    Kangasaurus_rex,
    Knightmare,
    Luchataur,
    Plated_scorpion,
    Shield_bugs,
    Tiger_squirrel,
    Urchin_hurler,
    killer_bee,
)


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
    )
    game.start_game()
    return game

#TODO - add tests for all card possible special effects

def test_bugserker_has_8_power_while_player_has_one_life_left() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    player.cards_laid_out = [Bugserker()]
    opponent.cards_laid_out = [Luchataur()]
    player.number_of_lives = 1

    game._recalculate_ongoing_effects()

    assert player.cards_laid_out[0].strength == 11
    assert opponent.cards_laid_out[0].strength == 9


def test_kangasaurus_rex_does_not_defeat_creatures_with_strength_equal_or_lower_than_4_when_opponent_has_deathweaver_in_cards_laid_out() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    weak_enemy_cards = [
        Chameleon_sniper(),  # 1
        Ferret_bomber(),  # 2
        Tiger_squirrel(),  # 3
        Plated_scorpion(),  # 2, TOUGH
        Deathweaver(),  # 2, POISONOUS
    ]
    strong_enemy_card = Luchataur()  # 9

    player.hand = [Kangasaurus_rex()]
    opponent.cards_laid_out = [*weak_enemy_cards, strong_enemy_card]

    game.play_card(hand_index=0)

    assert all(card in opponent.cards_laid_out for card in weak_enemy_cards)
    assert strong_enemy_card in opponent.cards_laid_out
    assert all(card not in opponent.discard_pile for card in weak_enemy_cards)
    assert strong_enemy_card not in opponent.discard_pile


def test_froblin_instigator_gets_plus_2_for_each_other_allied_creature() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    froblin = Froblin_instigator()
    player.cards_laid_out = [froblin, Chameleon_sniper(), Ferret_bomber()]
    opponent.cards_laid_out = [Luchataur()]

    game._recalculate_ongoing_effects()

    assert froblin.strength == 5


def test_ferret_pacifier_enemy_highest_power_creatures_cannot_block() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    highest_1 = Luchataur()
    highest_2 = Luchataur()
    lower = Kangasaurus_rex()

    player.cards_laid_out = [Ferret_pacifier()]
    opponent.cards_laid_out = [highest_1, lower, highest_2]

    game._recalculate_ongoing_effects()

    assert highest_1.cannot_block is True
    assert highest_2.cannot_block is True
    assert lower.cannot_block is False


def test_shield_bugs_gives_other_allied_creatures_plus_1_power() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    ally_1 = Chameleon_sniper()
    ally_2 = Ferret_bomber()
    shield_bugs = Shield_bugs()

    player.cards_laid_out = [shield_bugs, ally_1, ally_2]
    opponent.cards_laid_out = [Luchataur()]

    game._recalculate_ongoing_effects()

    assert shield_bugs.strength == 4
    assert ally_1.strength == 2
    assert ally_2.strength == 3


def test_urchin_hurler_buff_applies_only_during_owner_turn() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    ally_1 = Chameleon_sniper()
    ally_2 = Ferret_bomber()
    urchin_hurler = Urchin_hurler()

    player.cards_laid_out = [urchin_hurler, ally_1, ally_2]
    opponent.cards_laid_out = [Luchataur()]

    game._recalculate_ongoing_effects()
    assert ally_1.strength == 3
    assert ally_2.strength == 4

    game.end_turn()

    assert ally_1.strength == 1
    assert ally_2.strength == 2


def test_knightmare_prevents_its_owner_from_losing_life_from_direct_attack() -> None:
    game = _new_game()
    protected_player = game.players[0]
    attacking_player = game.players[1]

    protected_player.cards_laid_out = [Knightmare()]
    attacking_player.cards_laid_out = [Luchataur()]
    game.turn = 1

    game.attack(attacker_index=0)

    assert protected_player.number_of_lives == 3


def test_knightmare_prevents_its_owner_from_losing_life_from_card_effects() -> None:
    game = _new_game()
    protected_player = game.players[0]
    attacking_player = game.players[1]

    protected_player.cards_laid_out = [Knightmare()]
    attacking_player.hand = [killer_bee()]
    game.turn = 1

    game.play_card(hand_index=0)

    assert protected_player.number_of_lives == 3