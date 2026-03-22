from base_classes import DrawPile, Game
from cards import (
    Chameleon_sniper,
    Ferret_bomber,
    Kangasaurus_rex,
    Luchataur,
    Mindbug_bug,
    Plated_scorpion,
    Tiger_squirrel,
)


def test_opponent_steals_kangasaurus_rex_with_mindbug_and_activates_its_play_action_to_destroy_all_creatures_with_strength_less_than_or_equal_to_4() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent

    plated_scorpion = Plated_scorpion()  # 2, TOUGH (survives, charge goes to 0)
    plated_scorpion_without_tough = Plated_scorpion()  # 2, TOUGH but no charges
    plated_scorpion_without_tough.tough_charges = 0
    plated_scorpion_without_tough.description = "No TOUGH charges"
    weak_player_cards = [
        Chameleon_sniper(),  # 1
        Ferret_bomber(),  # 2
        Tiger_squirrel(),  # 3
        plated_scorpion,
        plated_scorpion_without_tough,
    ]
    strong_player_card = Luchataur()  # 9

    player.hand = [Kangasaurus_rex()]
    player.cards_laid_out = [*weak_player_cards, strong_player_card]

    game.play_card(hand_index=0)
    game.respond_to_mindbug(True)

    assert opponent.mindbugs_remaining == 1
    assert any(isinstance(card, Kangasaurus_rex) for card in opponent.cards_laid_out)
    assert strong_player_card in player.cards_laid_out
    assert any(card is plated_scorpion for card in player.cards_laid_out)
    assert plated_scorpion.tough_charges == 0
    assert all(card is not plated_scorpion_without_tough for card in player.cards_laid_out)
    assert any(card is plated_scorpion_without_tough for card in player.discard_pile)
    assert all(
        any(discarded_card is card for discarded_card in player.discard_pile)
        for card in weak_player_cards
        if card is not plated_scorpion
    )
    assert all(card is not plated_scorpion for card in player.discard_pile)


def test_multiplayer_mindbug_steal_does_not_consume_active_players_turn_action() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
        enforce_turn_action_limit=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent

    tiger_squirrel = Tiger_squirrel()
    player.hand = [Chameleon_sniper()]
    player.cards_laid_out = [tiger_squirrel]
    opponent.hand = [Chameleon_sniper(), Luchataur()]

    game.play_card(hand_index=0)
    game.respond_to_mindbug(True)

    assert game.current_player is player
    assert game._turn_action_taken is False

    game.attack(attacker_index=0)
    game.defend(None)

    assert tiger_squirrel in player.cards_laid_out
    assert opponent.number_of_lives == game.starting_lives - 1


def test_multiplayer_declined_mindbug_automatically_passes_turn() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
        enforce_turn_action_limit=True,
        auto_end_turn_after_successful_play=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent

    player.hand = [Chameleon_sniper()]
    opponent.hand = [Luchataur()]

    game.play_card(hand_index=0)
    game.respond_to_mindbug(False)

    assert game.current_player is opponent
    assert game.game_state == game.game_state.START_TURN
    assert game._turn_action_taken is False
    assert any(isinstance(card, Chameleon_sniper) for card in player.cards_laid_out)


def test_mindbug_bug_makes_opponent_lose_1_life_before_using_mindbug() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent

    player.hand = [Chameleon_sniper()]
    player.cards_laid_out = [Mindbug_bug()]
    opponent.hand = [Luchataur()]

    game.play_card(hand_index=0)
    game.respond_to_mindbug(True)

    assert opponent.number_of_lives == game.starting_lives - 1
    assert opponent.mindbugs_remaining == 1
    assert any(isinstance(card, Chameleon_sniper) for card in opponent.cards_laid_out)


def test_mindbug_bug_can_stop_mindbug_if_opponent_loses_last_life() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent

    player.hand = [Chameleon_sniper()]
    player.cards_laid_out = [Mindbug_bug()]
    opponent.hand = [Luchataur()]
    opponent.number_of_lives = 1

    game.play_card(hand_index=0)
    game.respond_to_mindbug(True)

    assert game.game_state == game.game_state.GAME_OVER
    assert game.winner is player
    assert opponent.mindbugs_remaining == 2
    assert not any(isinstance(card, Chameleon_sniper) for card in opponent.cards_laid_out)


def test_play_draws_replacement_before_pending_mindbug_response() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
        await_mindbug_response=True,
    )
    game.start_game(card_pool=[])

    player = game.current_player
    opponent = game.opponent
    replacement_card = Luchataur()

    player.hand = [
        Chameleon_sniper(),
        Tiger_squirrel(),
        Ferret_bomber(),
        Plated_scorpion(),
        Kangasaurus_rex(),
    ]
    player.draw_pile = DrawPile([replacement_card])
    opponent.hand = [Mindbug_bug()]

    game.play_card(hand_index=0)

    assert game._pending_mindbug_decision is not None
    assert len(player.hand) == 5
    assert replacement_card in player.hand