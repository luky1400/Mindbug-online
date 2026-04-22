from base_classes import DrawPile, Game
from unittest.mock import patch
from cards import (
    Axolotl_healer,
    Brain_fly,
    Chameleon_sniper,
    Compost_dragon,
    Ferret_bomber,
    Future_eric,
    Goreagle_alpha,
    Grave_robber,
    Hyenix,
    Hungry_hungry_hamster,
    Killer_bee,
    Kangasaurus_rex,
    Mysterious_mermaid,
    Plated_scorpion,
    Luchataur,
    Tiger_squirrel,
    Giraffodile,
)
from enums import GameState

def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
    )
    game.start_game()
    return game


def test_play_kangasaurus_rex_defeats_all_enemy_creatures_with_power_4_or_less() -> None:
    game = _new_game()

    player = game.current_player
    opponent = game.opponent

    plated_scorpion = Plated_scorpion()  # 2, TOUGH (survives, charge goes to 0)
    plated_scorpion_without_tough = Plated_scorpion()  # 2, TOUGH but no charges
    plated_scorpion_without_tough.tough_charges = 0
    plated_scorpion_without_tough.description = "No TOUGH charges"
    weak_enemy_cards = [
        Chameleon_sniper(),  # 1
        Ferret_bomber(),  # 2
        Tiger_squirrel(),  # 3
        plated_scorpion,
        plated_scorpion_without_tough,
    ]
    strong_enemy_card = Luchataur()  # 9

    player.hand = [Kangasaurus_rex()]
    opponent.cards_laid_out = [*weak_enemy_cards, strong_enemy_card]

    game.play_card(hand_index=0)
  
    # TODO - check if all asserts make sense
    assert any(card is plated_scorpion for card in opponent.cards_laid_out)
    assert plated_scorpion.tough_charges == 0
    assert all(card is not plated_scorpion_without_tough for card in opponent.cards_laid_out)
    assert any(card is plated_scorpion_without_tough for card in opponent.discard_pile)
    assert strong_enemy_card in opponent.cards_laid_out
    assert all(
        any(discarded_card is card for discarded_card in opponent.discard_pile)
        for card in weak_enemy_cards
        if card is not plated_scorpion
    )
    assert all(card is not plated_scorpion for card in opponent.discard_pile)


def test_play_giraffodile_draws_entire_discard_pile() -> None:
    game = _new_game()

    player = game.current_player
    discard_cards = [
        Chameleon_sniper(),
        Ferret_bomber(),
        Tiger_squirrel(),
    ]

    player.discard_pile = discard_cards.copy()
    player.hand = [Giraffodile(), Luchataur()]

    game.play_card(hand_index=0)

    assert player.discard_pile == []
    assert all(card in player.hand for card in discard_cards)
    assert len(player.hand) == 1 + len(discard_cards)


def test_play_axolotl_healer_player_gains_2_lifes() -> None:
    game = _new_game()

    player = game.current_player
    player.number_of_lives = 4
    player.hand = [Axolotl_healer()]

    game.play_card(hand_index=0)

    assert player.number_of_lives == 6


def test_play_ferret_bomber_opponent_discards_2_and_draws_if_possible() -> None:
    game = _new_game()

    player = game.current_player
    opponent = game.opponent

    opponent_hand_cards = [Chameleon_sniper(), Tiger_squirrel()]
    opponent_draw_pile_cards = [Axolotl_healer(), Luchataur()]
    all_opponent_cards = opponent_hand_cards + opponent_draw_pile_cards

    opponent.hand = opponent_hand_cards.copy()
    opponent.discard_pile = []
    opponent.draw_pile = DrawPile([])
    opponent.draw_pile.cards = opponent_draw_pile_cards.copy()
    player.hand = [Ferret_bomber()]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([0, 1])

    assert len(opponent.discard_pile) == 2
    assert len(opponent.hand) == 2
    assert all(
        any(card is zone_card for zone_card in opponent.hand + opponent.discard_pile)
        for card in all_opponent_cards
    )
    assert len(opponent.draw_pile.cards) == 0


def test_play_ferret_bomber_lets_opponent_choose_discarded_cards_when_more_than_two_are_in_hand() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hand_card_1 = Chameleon_sniper()
    hand_card_2 = Tiger_squirrel()
    hand_card_3 = Axolotl_healer()
    draw_card_1 = Luchataur()
    draw_card_2 = Giraffodile()

    opponent.hand = [hand_card_1, hand_card_2, hand_card_3]
    opponent.draw_pile = DrawPile([draw_card_1, draw_card_2])
    player.hand = [Ferret_bomber()]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([0, 2])

    assert hand_card_1 in opponent.discard_pile
    assert hand_card_3 in opponent.discard_pile
    assert hand_card_2 in opponent.hand
    assert draw_card_1 in opponent.hand
    assert draw_card_2 in opponent.hand


def test_play_killer_bee_opponent_loses_1_life() -> None:
    game = _new_game()

    player = game.current_player
    opponent = game.opponent
    opponent.number_of_lives = 4
    player.hand = [Killer_bee()]

    game.play_card(hand_index=0)

    assert opponent.number_of_lives == 3


def test_play_killer_bee_loses_last_life_and_opponent_loses_game() -> None:
    game = _new_game()

    player = game.current_player
    opponent = game.opponent
    opponent.number_of_lives = 1
    player.hand = [Killer_bee()]

    game.play_card(hand_index=0)

    assert opponent.number_of_lives == 0
    assert game.game_state == GameState.GAME_OVER
    assert game.winner == player


def test_play_mysterious_mermaid_sets_life_equal_to_opponent() -> None:
    game = _new_game()

    player = game.current_player
    opponent = game.opponent
    player.number_of_lives = 2
    opponent.number_of_lives = 5
    player.hand = [Mysterious_mermaid()]

    game.play_card(hand_index=0)

    assert player.number_of_lives == opponent.number_of_lives


def test_play_goreagle_alpha_player_loses_1_life() -> None:
    game = _new_game()

    player = game.current_player
    player.number_of_lives = 5
    player.hand = [Goreagle_alpha()]

    # NOTE - this is necessary, otherwise opponent has no cards left and game is over - evaluated in play_card method
    opponent = game.opponent
    opponent.hand = [Chameleon_sniper(), Tiger_squirrel()]

    game.play_card(hand_index=0)

    assert player.number_of_lives == 4
    assert game.game_state == GameState.ACTIVE


def test_play_goreagle_alpha_loses_last_life_and_player_loses_game() -> None:
    game = _new_game()

    player = game.current_player
    player.number_of_lives = 1
    player.hand = [Goreagle_alpha()]    
    
    opponent = game.opponent
    # NOTE - this is necessary, otherwise opponent has no cards left and game is over - evaluated in play_card method
    opponent.hand = [Chameleon_sniper(), Tiger_squirrel()]

    game.play_card(hand_index=0)

    assert player.number_of_lives == 0
    assert game.game_state == GameState.GAME_OVER
    assert game.winner == opponent


def test_play_brain_fly_takes_control_of_creature_with_power_6_or_more() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    stolen_creature = Luchataur()
    other_eligible_creature = Giraffodile()
    weak_creature = Ferret_bomber()
    player.hand = [Brain_fly()]
    opponent.cards_laid_out = [stolen_creature, other_eligible_creature, weak_creature]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([0])

    assert stolen_creature in player.cards_laid_out
    assert stolen_creature not in opponent.cards_laid_out
    assert other_eligible_creature in opponent.cards_laid_out
    assert weak_creature in opponent.cards_laid_out


def test_play_hungry_hungry_hamster_lets_opponent_choose_card_to_give() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    ignored_card = Tiger_squirrel()
    chosen_card = Chameleon_sniper()
    drawn_card = Axolotl_healer()
    player.hand = [Hungry_hungry_hamster()]
    opponent.hand = [ignored_card, chosen_card]
    opponent.draw_pile = DrawPile([drawn_card])

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([1])
    game.resolve_pending_card_action([0])

    assert chosen_card in player.hand
    assert ignored_card in opponent.hand
    assert chosen_card not in opponent.hand
    assert drawn_card in opponent.hand


def test_play_hungry_hungry_hamster_lets_player_play_received_card() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    received_card = Axolotl_healer()
    player.number_of_lives = 3
    player.hand = [Hungry_hungry_hamster()]
    opponent.hand = [received_card, Tiger_squirrel()]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([0])
    game.resolve_pending_card_action([1])

    assert player.number_of_lives == 5
    assert received_card in player.cards_laid_out
    assert received_card not in opponent.hand


def test_hyenix_can_be_played_from_discard_after_owner_loses_life() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hyenix = Hyenix()
    player.number_of_lives = 3
    player.discard_pile = [hyenix]
    player.hand = [Goreagle_alpha()]
    opponent.hand = [Tiger_squirrel()]

    game.play_card(hand_index=0)

    assert game._pending_card_action_choice is not None
    game.resolve_pending_card_action([1])

    assert player.number_of_lives == 2
    assert hyenix in player.cards_laid_out
    assert hyenix not in player.discard_pile


def test_hyenix_can_stay_in_discard_after_owner_loses_life() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hyenix = Hyenix()
    player.number_of_lives = 3
    player.discard_pile = [hyenix]
    player.hand = [Goreagle_alpha()]
    opponent.hand = [Tiger_squirrel()]

    game.play_card(hand_index=0)

    assert game._pending_card_action_choice is not None
    game.resolve_pending_card_action([0])

    assert player.number_of_lives == 2
    assert hyenix in player.discard_pile
    assert hyenix not in player.cards_laid_out


def test_play_compost_dragon_plays_card_from_discard_and_triggers_its_play_action() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    discard_card = Axolotl_healer()
    player.number_of_lives = 3
    player.discard_pile = [discard_card]
    player.hand = [Compost_dragon()]
    # Keep game active for deterministic assertions.
    opponent.hand = [Chameleon_sniper()]

    game.play_card(hand_index=0)

    assert player.number_of_lives == 5
    assert any(isinstance(card, Compost_dragon) for card in player.cards_laid_out)
    assert discard_card in player.cards_laid_out
    assert discard_card not in player.discard_pile


def test_play_compost_dragon_lets_player_choose_card_from_discard_pile() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    ignored_card = Chameleon_sniper()
    chosen_card = Axolotl_healer()
    starting_turn = game.turn
    player.number_of_lives = 3
    player.discard_pile = [ignored_card, chosen_card]
    player.hand = [Compost_dragon()]
    opponent.hand = [Tiger_squirrel()]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([1])

    assert chosen_card in player.cards_laid_out
    assert chosen_card not in player.discard_pile
    assert ignored_card in player.discard_pile
    assert player.number_of_lives == 5


def test_play_compost_dragon_resolves_discard_choice_with_turn_limit_enabled() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        enforce_turn_action_limit=True,
        auto_end_turn_after_successful_play=True,
    )
    game.start_game()

    player = game.current_player
    opponent = game.opponent

    ignored_card = Chameleon_sniper()
    chosen_card = Axolotl_healer()
    starting_turn = game.turn
    player.number_of_lives = 3
    player.discard_pile = [ignored_card, chosen_card]
    player.hand = [Compost_dragon()]
    opponent.hand = [Tiger_squirrel()]

    game.play_card(hand_index=0)
    game.resolve_pending_card_action([1])

    assert chosen_card in player.cards_laid_out
    assert ignored_card in player.discard_pile
    assert game.turn != starting_turn


def test_play_grave_robber_plays_card_from_opponent_discard_and_triggers_its_play_action() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    stolen_card = Axolotl_healer()
    other_discard_card = Ferret_bomber()
    player.number_of_lives = 3
    player.hand = [Grave_robber()]
    opponent.discard_pile = [stolen_card, other_discard_card]
    # Keep game active.
    opponent.hand = [Tiger_squirrel()]

    game.play_card(hand_index=0)
    # Eligible indices are [0, 1]; choose stolen_card (index 0 = Axolotl_healer).
    game.resolve_pending_card_action([0])

    assert player.number_of_lives == 5
    assert any(isinstance(card, Grave_robber) for card in player.cards_laid_out)
    assert stolen_card in player.cards_laid_out
    assert stolen_card not in opponent.discard_pile
    assert other_discard_card in opponent.discard_pile


def test_play_future_eric_refills_hand_from_cards_it_added_to_draw_pile() -> None:
    # Regression: Future Eric's PLAY effect adds 2 cards to the bottom of the draw pile,
    # then the game must refill the hand using those just-added cards.
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    player.hand = [Future_eric()]
    player.draw_pile = DrawPile([])
    bottom_card_a = Tiger_squirrel()
    bottom_card_b = Ferret_bomber()
    game.unused_pile = [bottom_card_a, bottom_card_b]
    opponent.hand = [Chameleon_sniper()]

    game.play_card(hand_index=0)

    # Future Eric is on board, both unused-pile cards entered the draw pile,
    # and the hand was refilled to the limit (5) from those cards.
    assert any(c.name == "Future Eric" for c in player.cards_laid_out)
    assert game.unused_pile == []
    assert len(player.hand) == min(
        game.hand_size_limit, len([bottom_card_a, bottom_card_b])
    )
    assert bottom_card_a in player.hand
    assert bottom_card_b in player.hand


def test_play_tiger_squirrel_defeats_enemy_creature_with_power_7_or_more() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    strong_enemy = Luchataur()
    weak_enemy = Ferret_bomber()
    player.hand = [Tiger_squirrel()]
    opponent.cards_laid_out = [weak_enemy, strong_enemy]
    # Keep game active.
    opponent.hand = [Chameleon_sniper()]

    game.play_card(hand_index=0)

    assert strong_enemy in opponent.discard_pile
    assert strong_enemy not in opponent.cards_laid_out
    assert weak_enemy in opponent.cards_laid_out


