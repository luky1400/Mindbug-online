from base_classes import Game
from cards import Creep_from_the_deep, Ferret_bomber, Luchataur

# Question: Can HUNTER attack cards that cannot block (e.g. Elephantopus forbits)?
# Answer: "S Lovcem stále můžete ulovit jakoukoliv příšeru chcete. Chapaslon jen brání soupeři, aby si vybral tu příšeru jako obránce. Nicméně, použití schopnosti Lovec je dobrovolné. Takže, pokud se rozhodnete schopnost Lovec při svém útoku nevyužít a soupeř má jen příšery se silou 4 nebo méně, váš Lovec bude neblokovatelný."


def _new_game() -> Game:
    game = Game(
        player_names=["Player 1", "Player 2"],
        starting_draw_pile_size=0,
    )
    game.start_game(card_pool=[])
    return game


def test_hunter_attacker_can_target_enemy_creature_that_cannot_block() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hunter_attacker = Creep_from_the_deep()  # HUNTER + POISONOUS
    target = Luchataur()
    target.cannot_block = True

    player.cards_laid_out = [hunter_attacker]
    opponent.cards_laid_out = [target]

    game.attack(attacker_index=0, defender_index=0)

    assert target not in opponent.cards_laid_out
    assert target in opponent.discard_pile


def test_hunter_attacker_has_all_enemy_creatures_as_eligible_targets() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hunter_attacker = Creep_from_the_deep()
    defender_1 = Ferret_bomber()
    defender_1.cannot_block = True
    defender_2 = Luchataur()

    player.cards_laid_out = [hunter_attacker]
    opponent.cards_laid_out = [defender_1, defender_2]

    eligible = game.get_eligible_defender_indices(attacker_index=0)

    assert eligible == [0, 1]


def test_hunter_attacker_can_skip_hunter_override_and_use_only_legal_blockers() -> None:
    game = _new_game()
    player = game.current_player
    opponent = game.opponent

    hunter_attacker = Creep_from_the_deep()
    hunter_attacker.min_blocker_strength = 7
    ineligible_blocker = Ferret_bomber()
    legal_blocker = Luchataur()

    player.cards_laid_out = [hunter_attacker]
    opponent.cards_laid_out = [ineligible_blocker, legal_blocker]

    eligible_when_skipping_hunter = game.get_eligible_defender_indices(
        attacker_index=0, hunter_target_override=False
    )

    assert eligible_when_skipping_hunter == [1]
