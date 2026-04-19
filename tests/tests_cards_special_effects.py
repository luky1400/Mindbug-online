import pytest

from base_classes import Game
from cards import (
    Bee_bear,
    Brain_fly,
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
    Shark_dog,
    Shield_bugs,
    Tiger_squirrel,
    Urchin_hurler,
    Watts_dog,
    Wolfman_steve,
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


def test_watts_dog_can_only_be_blocked_by_creatures_with_no_special_types() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    watts_dog = Watts_dog()
    plain_blocker = Brain_fly()  # no special types
    keyword_blocker_1 = Ferret_bomber()  # SNEAKY
    keyword_blocker_2 = Shark_dog()  # HUNTER

    player.cards_laid_out = [watts_dog]
    opponent.cards_laid_out = [keyword_blocker_1, plain_blocker, keyword_blocker_2]

    eligible = game.get_eligible_defender_indices(attacker_index=0)

    assert eligible == [1]


def test_watts_dog_attack_rejects_blocker_with_special_types() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    player.cards_laid_out = [Watts_dog()]
    opponent.cards_laid_out = [Ferret_bomber()]  # SNEAKY

    game.attack(attacker_index=0)

    with pytest.raises(ValueError):
        game.defend(defender_index=0)


def test_watts_dog_attack_accepts_blocker_with_no_special_types() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    watts_dog = Watts_dog()  # strength 5
    plain_blocker = Bee_bear()  # strength 8, no special types

    player.cards_laid_out = [watts_dog]
    opponent.cards_laid_out = [plain_blocker]

    game.attack(attacker_index=0)
    game.defend(defender_index=0)

    assert watts_dog in player.discard_pile
    assert plain_blocker in opponent.cards_laid_out


def test_knightmare_prevents_its_owner_from_losing_life_from_card_effects() -> None:
    game = _new_game()
    protected_player = game.players[0]
    attacking_player = game.players[1]

    protected_player.cards_laid_out = [Knightmare()]
    attacking_player.hand = [killer_bee()]
    game.turn = 1

    game.play_card(hand_index=0)

    assert protected_player.number_of_lives == 3


def test_wolfman_steve_blocks_opponent_from_playing_weak_cards_from_hand() -> None:
    game = _new_game()
    owner = game.players[0]
    opponent = game.players[1]

    owner.cards_laid_out = [Wolfman_steve()]
    weak_card = Brain_fly()  # strength 4
    opponent.hand = [weak_card]
    game.turn = 1

    with pytest.raises(ValueError):
        game.play_card(hand_index=0)

    assert weak_card in opponent.hand


def test_wolfman_steve_allows_opponent_to_play_strong_cards_from_hand() -> None:
    game = _new_game()
    owner = game.players[0]
    opponent = game.players[1]

    owner.cards_laid_out = [Wolfman_steve()]
    strong_card = Luchataur()  # strength 9
    opponent.hand = [strong_card]
    game.turn = 1

    game.play_card(hand_index=0)

    assert strong_card in opponent.cards_laid_out
    assert strong_card not in opponent.hand


def test_wolfman_steve_does_not_restrict_its_owner() -> None:
    game = _new_game()
    owner = game.players[0]

    owner.cards_laid_out = [Wolfman_steve()]
    weak_card = Brain_fly()  # strength 4
    owner.hand = [weak_card]
    game.turn = 0

    game.play_card(hand_index=0)

    assert weak_card in owner.cards_laid_out


def test_wolfman_steve_restriction_lifts_when_removed_from_battlefield() -> None:
    game = _new_game()
    owner = game.players[0]
    opponent = game.players[1]

    wolfman = Wolfman_steve()
    owner.cards_laid_out = [wolfman]
    weak_card = Brain_fly()  # strength 4
    opponent.hand = [weak_card]
    game.turn = 1

    owner.cards_laid_out = []
    owner.discard_pile = [wolfman]

    game.play_card(hand_index=0)

    assert weak_card in opponent.cards_laid_out