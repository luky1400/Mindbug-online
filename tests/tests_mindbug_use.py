from base_classes import Game
from cards import (
    Chameleon_sniper,
    Ferret_bomber,
    Kangasaurus_rex,
    Luchataur,
    Plated_scorpion,
    Tiger_squirrel,
)


def test_opponent_steals_kangasaurus_rex_with_mindbug_and_activates_its_play_action_to_destroy_all_creatures_with_strength_less_than_or_equal_to_4() -> None:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_hand_size=0,
        starting_draw_pile_size=0,
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

    was_stolen = game.play_card(hand_index=0, use_opponent_mindbug=True)

    assert was_stolen is True
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