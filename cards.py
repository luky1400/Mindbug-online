from base_classes import Card
from enums import CardActionType, CardSet, CardSpecialType, GameState
from typing import Optional
from collections.abc import Callable
from base_classes import Game
from random import randint
import random


def _build_card_pool(card_specs: list[tuple[Callable[[], Card], int]]) -> list[Card]:
    card_pool: list[Card] = []
    for card_factory, copies in card_specs:
        card_pool.extend(card_factory() for _ in range(copies))
    return card_pool


# SOURCE: https://ryanascherr.github.io/mindbug/
# IMG: https://github.com/ryanascherr/mindbug-deck/tree/main
# # copies: https://mindbug.fandom.com/wiki/First_Contact, https://mindbug.fandom.com/wiki/First_Contact_Addon_Pack
# Additional Promo Cards: https://mindbug.fandom.com/wiki/Promo_Cards
def get_card_pool(sets: list[CardSet] | None = None) -> list[Card]:
    if sets is None:
        sets = [CardSet.FIRST_CONTACT, CardSet.NEW_SERVANTS, CardSet.PROMO_CARDS]
    card_pool = _build_card_pool(
        [
            # CardSet.FIRST_CONTACT - includes 48/49 cards
            (Axolotl_healer, 2),
            (Bee_bear, 1),
            (Brain_fly, 1),
            (Chameleon_sniper, 1),
            (Compost_dragon, 2),
            (Deathweaver, 1),
            (Elephantopus, 1),
            (Explosive_toad, 2),
            (Ferret_bomber, 2),
            (Giraffodile, 1),
            (Goblin_werewolf, 2),
            (Gorillion, 1),
            (Grave_robber, 2),
            (Harpy_mother, 1),
            (Kangasaurus_rex, 2),
            (killer_bee, 2),
            (Lone_yeti, 1),
            (Luchataur, 2),
            (Mysterious_mermaid, 1),
            (Plated_scorpion, 2),
            (Rhino_turtle, 2),
            (Shark_dog, 1),
            (Sharky_crab_dog_mummypus, 1),
            (Shield_bugs, 2),
            (
                Short_neck_giraffodile,
                1,
            ),  # = nerfed version of Giraffodile (exclusive for online Mindbug) - replace Girafoddile/add to Add-ons set?
            (Snail_hydra, 2),
            (Snail_thrower, 1),
            (Spider_owl, 2),
            (Strange_barrel, 1),
            (Tiger_squirrel, 2),
            (Turbo_bug, 1),
            (Tusked_extorter, 2),
            (Urchin_hurler, 1),
            # CardSet.NEW_SERVANTS - includes 24 cards
            (Bugserker, 2),
            (Count_draculeech, 2),
            (Creep_from_the_deep, 2),
            (Ferret_pacifier, 2),
            (Froblin_instigator, 2),
            (Goreagle_alpha, 2),
            (Hamster_lion, 2),
            (Hungry_hungry_hamster, 2),
            (Hyenix, 2),
            (Majestic_manticore, 2),
            (The_lurker, 2),
            (Turf_the_surfer, 2),
            # CardSet.PROMO_CARDS
            (Battle_beetle, 1),
            (Boar_zooka, 1),
            # (Evilcat, 1), # NOTE - this is 3rd evolution
            (Future_eric, 1),
            (Knightmare, 1),
            (Macaw_dagon, 1),
            (Mindbug_bug, 1),
            (Ram_hopper, 1),
            (Steamforger, 1),
            (The_pack, 1),
            (Unigon, 1),
            (Wheatl_e, 1),
        ]
    )
    allowed_sets = set(sets)
    return [card for card in card_pool if card.set in allowed_sets]


# class Alien_brain(Card):
#     name: str = "Alien Brain"
#     strength: int = 3
#     special_types: list[CardSpecialType] = [CardSpecialType.POISONOUS]
#     description: str = "Opponent cannot put cards into their hand."
#     set: CardSet = CardSet.PROMO_CARDS

#     # TODO
#     def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
#         opponent.cannot_put_cards_into_hand = True


# # Hard
# class Alpacoodle(Card):
#     name: str = "Alpacoodle"
#     strength: int = 2
#     special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
#     action_type: CardActionType = CardActionType.PLAY # TODO
#     play_action_description: str = "Set aside all other creatures."
#     defeated_action_description: str = "Return them to play without activating their Play effects."
#     set: CardSet = CardSet.PROMO_CARDS


class Axolotl_healer(Card):
    name: str = "Axolotl Healer"
    strength: int = 4
    special_types: list[CardSpecialType] = [CardSpecialType.POISONOUS]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Gain 2 lifes."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.current_player.number_of_lives = game.current_player.number_of_lives + 2
        game.log.append(f"{game.current_player.name} gains 2 lives.")


class Battle_beetle(Card):
    name: str = "Battle Beetle"
    strength: int = 8
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = (
        "If you have the same number of Mindbugs as the opponent, the opponent loses 2 lives."
    )
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        if game.current_player.mindbugs_remaining == game.opponent.mindbugs_remaining:
            lost_life = game.lose_life(1 - game.turn, 2, auto_end_after_attack=True)
            if lost_life > 0:
                game.log.append(
                    f"{game.opponent.name} loses {lost_life} lives because {game.current_player.name} plays Battle Beetle."
                )
            else:
                game.log.append(f"{game.opponent.name} cannot lose life.")
        else:
            game.log.append(
                f"{game.opponent.name} does not lose 2 lives because you have a different number of Mindbugs."
            )


class Bee_bear(Card):
    name: str = "Bee Bear"
    strength: int = 8
    special_types: list[CardSpecialType] = []
    description: str = "Cannot be blocked by creatures with power 6 or less."
    min_blocker_strength: int = 7
    set: CardSet = CardSet.FIRST_CONTACT


class Boar_zooka(Card):
    name: str = "Boar Zooka"
    strength: int = 6
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.DEFEATED
    action_description: str = "Defeat all enemy creatures."
    description: str = "Cannot block."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        for card in game.opponent.cards_laid_out.copy():
            game._destroy_creature(game.opponent, card)
        game.log.append(
            f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} defeats all enemy creatures."
        )

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        self.cannot_block = True


class Brain_fly(Card):
    name: str = "Brain Fly"
    strength: int = 4
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Take control of a creature with power 6 or more."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_brain_fly_action(self)


class Bugserker(Card):
    name: str = "Bugserker"
    strength: int = 3
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    description: str = "Has +8 power while you have one life left."
    set: CardSet = CardSet.NEW_SERVANTS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if owner.number_of_lives == 1:
            self.strength += 8


class Compost_dragon(Card):
    name: str = "Compost Dragon"
    strength: int = 3
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Play a card from your discard pile."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_compost_dragon_action(self)


class Count_draculeech(Card):
    name: str = "Count Draculeech"
    strength: int = 7
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Lose 1 life. Defeat a creature of your choice."
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        lost_life = game.lose_life(game.turn, 1, auto_end_after_attack=True)
        if lost_life > 0:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} causes {game.current_player.name} to lose {lost_life} life."
            )
        else:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} would make its owner lose life, but they cannot lose life."
            )
        game.resolve_count_draculeech_action(self)


class Creep_from_the_deep(Card):
    name: str = "Creep from the Deep"
    strength: int = 4
    special_types: list[CardSpecialType] = [
        CardSpecialType.POISONOUS,
        CardSpecialType.HUNTER,
    ]
    set: CardSet = CardSet.NEW_SERVANTS


class Deathweaver(Card):
    name: str = "Deathweaver"
    strength: int = 2
    special_types: list[CardSpecialType] = [CardSpecialType.POISONOUS]
    description: str = "The opponent cannot activate play effects."
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        opponent.cannot_activate_play_effects = True


class Elephantopus(Card):
    name: str = "Elephantopus"
    strength: int = 7
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    description: str = "Opponent cannot block with creatures with power 4 or less."
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        opponent.cannot_block_with_creatures_with_power_4_or_less = True


class Evilcat(Card):
    name: str = "Evilcat"
    strength: int = 3
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "You win the game."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        game.game_state = GameState.GAME_OVER
        game.winner = game.current_player
        game.log.append(f"{game.current_player.name} wins the game with Evilcat.")


class Explosive_toad(Card):
    name: str = "Explosive Toad"
    strength: int = 5
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
    action_type: CardActionType = CardActionType.DEFEATED
    action_description: str = "Defeat a creature of your choice."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_explosive_toad_action(self)


class Ferret_bomber(Card):
    name: str = "Ferret Bomber"
    strength: int = 2
    special_types: list[CardSpecialType] = [CardSpecialType.SNEAKY]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "An opponent discards 2 cards from their hand."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_ferret_bomber_action(self)


class Ferret_pacifier(Card):
    name: str = "Ferret Pacifier"
    strength: int = 4
    special_types: list[CardSpecialType] = []
    description: str = "The enemy creature(s) with the highest power cannot block."
    set: CardSet = CardSet.NEW_SERVANTS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if len(opponent.cards_laid_out) > 0:
            opponent.cannot_block_with_creatures_with_highest_power = True


class Froblin_instigator(Card):
    name: str = "Froblin Instigator"
    strength: int = 1
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    description: str = "Has +2 power for each other allied creature."
    set: CardSet = CardSet.NEW_SERVANTS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        allied_creatures = max(0, len(owner.cards_laid_out) - 1)
        self.strength += 2 * allied_creatures


class Future_eric(Card):
    name: str = "Future Eric"
    strength: int = 3
    special_types: list[CardSpecialType] = [CardSpecialType.SNEAKY]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = (
        "Put the top 2 cards of the unused pile on the bottom of your draw pile without looking at them."
    )
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        cards_moved = 0
        for _ in range(2):
            if not game.unused_pile:
                break
            card = game.unused_pile.pop(0)
            game.current_player.draw_pile.add(card)
            cards_moved += 1
        if cards_moved > 0:
            game.log.append(
                f"{game.current_player.name} puts {cards_moved} card(s) from the unused pile on the bottom of their draw pile."
            )


class Giraffodile(Card):
    name: str = "Giraffodile"
    strength: int = 7
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Draw your entire dicard pile."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.current_player.hand.extend(game.current_player.discard_pile)
        game.current_player.discard_pile = []
        game.log.append(f"{game.current_player.name} draws their entire discard pile.")


class Goblin_werewolf(Card):
    name: str = "Goblin Werewolf"
    strength: int = 2
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    description: str = "Has +6 strength while it is your turn."
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if game.current_player is owner:
            self.strength += 6


class Gorillion(Card):
    name: str = "Gorillion"
    strength: int = 10
    special_types: list[CardSpecialType] = []
    description: Optional[str] = "Why did you take the bananas?"
    set: CardSet = CardSet.FIRST_CONTACT


class Goreagle_alpha(Card):
    name: str = "Goreagle Alpha"
    strength: int = 6
    special_types: list[CardSpecialType] = [
        CardSpecialType.FRENZY,
        CardSpecialType.TOUGH,
        CardSpecialType.HUNTER,
    ]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Lose 1 life."
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        lost_life = game.lose_life(game.turn, 1, auto_end_after_play=True)
        if lost_life > 0:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} causes {game.current_player.name} to lose {lost_life} life."
            )
        else:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} would make its owner lose life, but they cannot lose life."
            )


class Grave_robber(Card):
    name: str = "Grave Robber"
    strength: int = 7
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Play a card from an opponent's discard pile."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_grave_robber_action(self)


class Hamster_lion(Card):
    name: str = "Hamster Lion"
    strength: int = 8
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
    description: str = "The enemy creature(s) with the lowest power cannot attack."
    set: CardSet = CardSet.NEW_SERVANTS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if len(opponent.cards_laid_out) > 0:
            opponent.cannot_attack_with_creatures_with_lowest_power = True


class Harpy_mother(Card):
    name: str = "Harpy Mother"
    strength: int = 5
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.DEFEATED
    action_description: str = (
        "Take control of up to 2 enemy creatures with power 5 or less."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_harpy_mother_action(self)


class Hungry_hungry_hamster(Card):
    name: str = "Hungry Hungry Hamster"
    strength: int = 2
    special_types: list[CardSpecialType] = [CardSpecialType.SNEAKY]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = (
        "An opponent gives you a card from their hand. Play it or put it into your hand."
    )
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        game.resolve_hungry_hungry_hamster_action(self)


class Hyenix(Card):
    name: str = "Hyenix"
    strength: int = 7
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
    description: str = (
        "When you lose life while this is in your discard pile, you may play this card."
    )
    set: CardSet = CardSet.NEW_SERVANTS


# PROBLEM - https://boardgamegeek.com/thread/3176165/chuck-harpy-mother-interaction
# class Chuck(Card):
#     name: str = "Chuck"
#     strength: int = 3
#     special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
#     action_type: CardActionType = CardActionType.PLAY
#     action_description: str = "Roll a 6-sided die. On 4 to 6, defeat an enemy creature and then repeat this effect."
#     set: CardSet = CardSet.PROMO_CARDS

#     def trigger_action(self, game: Game) -> None:
#         roll = random.randint(1, 6)
#         if roll >= 4:
# TODO - Player choice
#             game._destroy_creature(game.opponent, game.opponent.cards_laid_out[0])
#             game.log.append(
#                 f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} rolls a {roll} and defeats {game.opponent.name}'s {game.opponent.cards_laid_out[0].name}."
#             )
#         else:
#             game.log.append(
#                 f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} rolls a {roll} and does not defeat an enemy creature."
#             )


class Chameleon_sniper(Card):
    name: str = "Chameleon Sniper"
    strength: int = 1
    special_types: list[CardSpecialType] = [CardSpecialType.SNEAKY]
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "The opponent loses 1 life."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        lost_life = game.lose_life(1 - game.turn, 1, auto_end_after_attack=True)
        if lost_life > 0:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} attacks {game.opponent.name} for {lost_life} life."
            )
        else:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} attacks {game.opponent.name}, but they cannot lose life."
            )


# class Ivybug(Card):
#     name: str = "Ivybug"
#     strength: int = 5
#     special_types: list[CardSpecialType] = []
#     description: str = "You may use your life as Mindbugs."
#     set: CardSet = CardSet.PROMO_CARDS

#     def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
#         # TODO - implement
#         pass


# class Jazz_dog(Card):
#     name: str = "Jazz Dog"
#     strength: int = 5
#     special_types: list[CardSpecialType] = []
#     description: str = "At the end of your turn, if an enemy creature blocked this turn and is still in play, take control of it ."
#     set: CardSet = CardSet.PROMO_CARDS

#     def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
#         for card in opponent.cards_laid_out:
#             if card.blocked_this_turn and card.is_in_play:
#                 game._destroy_creature(opponent, card)
#                 game.log.append(
#                     f"{game.current_player.name} takes control of {card.name} from {game.opponent.name}."
#                 )


# Hard
# class Jean_claw_pandamme(Card):
#     name: str = "Jean Claw Pandamme"
#     strength: int = 5
#     special_types: list[CardSpecialType] = []
#     description: str = "Enemy creatues have 'Attack: Discard a card'."
#     set: CardSet = CardSet.PROMO_CARDS

#     def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
#         for card in opponent.cards_laid_out:
#             # TODO
#             # Which attack effect trigger first when creature have 2 attack effects?
#             card.action_type = CardActionType.ATTACK
#             card.action_description = "Discard a card."


class Kangasaurus_rex(Card):
    name: str = "Kangasaurus Rex"
    strength: int = 7
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Defeat all enemy creatures with power 4 or less."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        # NOTE: we need to use iteration over a copy of the list, otherwise - when you remove items while looping, Python’s loop index advances but the list shrinks/reindexes, so some elements are skipped.
        for card in game.opponent.cards_laid_out.copy():
            if card.strength <= 4:
                game._destroy_creature(game.opponent, card)
        game.log.append(
            f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} defeats all enemy creatures with power 4 or less."
        )


class killer_bee(Card):
    name: str = "Killer Bee"
    strength: int = 5
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "The opponent loses 1 life."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        lost_life = game.lose_life(1 - game.turn, 1, auto_end_after_play=True)
        if lost_life > 0:
            game.log.append(
                f"{game.opponent.name} loses {lost_life} life because {game.current_player.name} plays Killer Bee."
            )
        else:
            game.log.append(f"{game.opponent.name} cannot lose life.")


class Knightmare(Card):
    name: str = "Knightmare"
    strength: int = 5
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    action_type: CardActionType = CardActionType.DEFEATED
    action_description: str = "You lose the game."
    description: str = "You cannot lose life."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        game.game_state = GameState.GAME_OVER
        game.winner = game.opponent
        game.log.append(
            f"{game.opponent.name} wins the game because {game.current_player.name}'s {self.name} was defeated."
        )

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        owner.cannot_lose_life = True


class Lone_yeti(Card):
    name: str = "Lone Yeti"
    strength: int = 5
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    description: str = (
        f"While this is your only allied creature, it has +5 power and {CardSpecialType.FRENZY.value}."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if len(owner.cards_laid_out) != 1:
            return
        self.strength += 5
        if CardSpecialType.FRENZY not in self.special_types:
            self.special_types.append(CardSpecialType.FRENZY)


class Luchataur(Card):
    name: str = "Luchataur"
    strength: int = 9
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
    description: str = "Want an encore?"
    set: CardSet = CardSet.FIRST_CONTACT


class Macaw_dagon(Card):
    name: str = "Macaw Dagon"
    strength: int = 8
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Swap hand with the opponent."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        game.current_player.hand, game.opponent.hand = (
            game.opponent.hand,
            game.current_player.hand,
        )
        game.log.append(
            f"{game.current_player.name} swaps their hand with {game.opponent.name}'s hand."
        )


class Majestic_manticore(Card):
    name: str = "Majestic Manticore"
    strength: int = 6
    special_types: list[CardSpecialType] = [CardSpecialType.POISONOUS]
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Defeat the creature(s) with the lowest power."
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        lowest_power = min(card.strength for card in game.opponent.cards_laid_out)
        # Iterate over a copy because _destroy_creature mutates cards_laid_out.
        for card in game.opponent.cards_laid_out.copy():
            if card.strength == lowest_power:
                game._destroy_creature(game.opponent, card)
        game.log.append(
            f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} defeats the creature(s) with the lowest power."
        )


class Mindbug_bug(Card):
    name: str = "Mindbug Bug"
    strength: int = 7
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    description: str = "When the opponent uses a Mindbug, they first lose 1 life."
    set: CardSet = CardSet.PROMO_CARDS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        opponent.life_loss_before_using_mindbug += 1


class Mysterious_mermaid(Card):
    name: str = "Mysterious Mermaid"
    strength: int = 7
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = "Set your life equal to the opponent's."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.current_player.number_of_lives = game.opponent.number_of_lives
        game.log.append(
            f"{game.current_player.name} sets their life equal to {game.opponent.name}'s life."
        )


class Plated_scorpion(Card):
    name: str = "Plated Scorpion"
    strength: int = 2
    special_types: list[CardSpecialType] = [
        CardSpecialType.TOUGH,
        CardSpecialType.POISONOUS,
    ]
    description: str = "That sting sticks."
    set: CardSet = CardSet.FIRST_CONTACT


class Ram_hopper(Card):
    name: str = "Ram Hopper"
    strength: int = 7
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
    description: str = f"Other allied creatures have {CardSpecialType.FRENZY.value}."
    set: CardSet = CardSet.PROMO_CARDS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        for card in owner.cards_laid_out:
            if card is not self:
                card.special_types.append(CardSpecialType.FRENZY)


# class Ratomanger(Card):
#     name: str = "Ratomanger"
#     strength: int = 2
#     special_types: list[CardSpecialType] = []
#     action_type: CardActionType = CardActionType.PLAY
#     action_description: str = "Play any number of cards with power 4 or less from your discard pile without activating their Play effects."
#     set: CardSet = CardSet.PROMO_CARDS

#     def trigger_action(self, game: Game) -> None:
#         # TODO - Player choice
#         game.resolve_ratomanger_action(self)


class Rhino_turtle(Card):
    name: str = "Rhino Turtle"
    strength: int = 8
    description: Optional[str] = "No shield can stop me."
    special_types: list[CardSpecialType] = [
        CardSpecialType.TOUGH,
        CardSpecialType.FRENZY,
    ]
    set: CardSet = CardSet.FIRST_CONTACT


class Shark_dog(Card):
    name: str = "Shark Dog"
    strength: int = 4
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = (
        "Defeat an enemy creature with power 6 or more of your choice."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_shark_dog_action(self)


class Sharky_crab_dog_mummypus(Card):
    name: str = "Sharky Crab Dog Mummypus"
    strength: int = 5
    special_types: list[CardSpecialType] = []
    description: str = (
        f"Has {CardSpecialType.HUNTER.value} while an enemy creature does. Repeat for {CardSpecialType.SNEAKY.value},{CardSpecialType.FRENZY.value}, and {CardSpecialType.POISONOUS.value}."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        copied_tags = [
            CardSpecialType.HUNTER,
            CardSpecialType.SNEAKY,
            CardSpecialType.FRENZY,
            CardSpecialType.POISONOUS,
        ]
        enemy_tags = {
            tag for card in opponent.cards_laid_out for tag in card.special_types
        }
        for tag in copied_tags:
            if tag in enemy_tags and tag not in self.special_types:
                self.special_types.append(tag)


class Shield_bugs(Card):
    name: str = "Shield Bugs"
    strength: int = 4
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    description: str = "Other allied creatures have +1 power."
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        for card in owner.cards_laid_out:
            if card is not self:
                card.strength += 1


class Short_neck_giraffodile(Card):
    name: str = "Short Neck Giraffodile"
    strength: int = 7
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Draw 2 cards from your discard pile."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_short_neck_giraffodile_action(self)


# class Slugapult(Card):
#     name: str = "Slugapult"
#     strength: int = 5
#     special_types: list[CardSpecialType] = [CardSpecialType.TOUGH, CardSpecialType.FRENZY]
#     action_type: CardActionType = CardActionType.ATTACK
#     action_description: str = "You may defeat another allied creature. If you do, defeat an enemy creature."
#     set: CardSet = CardSet.PROMO_CARDS

#     def trigger_action(self, game: Game) -> None:
#         # TODO - Player choice
#         game.resolve_slugapult_action(self)


# class Sluggernaut(Card):
#     name: str = "Sluggernaut"
#     strength: int = 6
#     special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
#     action_type: CardActionType = CardActionType.LOSE_TOUGH_CHARGE # TODO - add action_description
#     set: CardSet = CardSet.PROMO_CARDS

#     def trigger_action(self, game: Game) -> None:
#         # TODO - Player choice
#         game.resolve_sluggernaut_action(self)


class Snail_hydra(Card):
    name: str = "Snail Hydra"
    strength: int = 9
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = (
        "If you control fewer creatures than an opponent, defeat a creature of your choice."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        if len(game.current_player.cards_laid_out) < len(game.opponent.cards_laid_out):
            game.resolve_snail_hydra_action(self)
        else:
            game.log.append(
                f"{game.current_player.name}'s {self.name} does not defeat a creature."
            )


class Snail_thrower(Card):
    name: str = "Snail Thrower"
    strength: int = 1
    special_types: list[CardSpecialType] = [CardSpecialType.POISONOUS]
    description: str = (
        f"Other allied creatures with power 4 or less have {CardSpecialType.HUNTER.value} and {CardSpecialType.POISONOUS.value}."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        for card in owner.cards_laid_out:
            if card is self or card.strength > 4:
                continue
            if CardSpecialType.HUNTER not in card.special_types:
                card.special_types.append(CardSpecialType.HUNTER)
            if CardSpecialType.POISONOUS not in card.special_types:
                card.special_types.append(CardSpecialType.POISONOUS)


class Spider_owl(Card):
    name: str = "Spider Owl"
    strength: int = 3
    special_types: list[CardSpecialType] = [
        CardSpecialType.SNEAKY,
        CardSpecialType.POISONOUS,
    ]
    description: str = "Hanging in there."
    set: CardSet = CardSet.FIRST_CONTACT


class Strange_barrel(Card):
    name: str = "Strange Barrel"
    strength: int = 6
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.DEFEATED
    action_description: str = "Steal 2 random cards from an opponent's hand."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        for _ in range(2):
            if len(game.opponent.hand) > 0:
                card = game.opponent.hand.pop(randint(0, len(game.opponent.hand) - 1))
                game.current_player.hand.append(card)
                game.log.append(
                    f"{game.current_player.name} steals {card.name} from {game.opponent.name}'s hand."
                )
            else:
                game.log.append(
                    f"{game.current_player.name} cannot steal a card from {game.opponent.name}'s hand because they have no cards."
                )


# NOTE - I will need to do list for action_type and action_description, and make function: trigger_play_effect, trigger_attack_effect and trigger_defeated_effect
# class Suspicious_gift(Card):
#     name: str = "Suspicious Gift"
#     strength: int = 1
#     special_types: list[CardSpecialType] = []
#     action_types: list[CardActionType] = [CardActionType.PLAY, CardActionType.DEFEATED]
#     action_description: list[str] = ["An opponent takes control of this card.", "Lose 2 lives."] # TODO - how to know which description to display in UI when player choosing
#     set: CardSet = CardSet.PROMO_CARDS

#     def trigger_play_effect(self, game: Game) -> None:
#         game.opponent.cards_laid_out.append(self)
#         game.log.append(f"{game.opponent.name} takes control of {self.name}.")

#     def trigger_defeated_effect(self, game: Game) -> None:
#         game.opponent.lose_life(2)
#         game.log.append(f"{game.opponent.name} loses 2 lives.")


class Steamforger(Card):
    name: str = "Steamforger"
    strength: int = 9
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = (
        "If you control at least 3 more creatures than an opponent, you win the game."
    )
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        if (
            len(game.current_player.cards_laid_out)
            >= len(game.opponent.cards_laid_out) + 3
        ):
            game.game_state = GameState.GAME_OVER
            game.winner = game.current_player
            game.log.append(
                f"{game.current_player.name} wins the game with Steamforger."
            )
        else:
            game.log.append(
                f"{game.current_player.name} does not win the game with Steamforger."
            )


class The_lurker(Card):
    name: str = "The Lurker"
    strength: int = 4
    special_types: list[CardSpecialType] = [CardSpecialType.TOUGH]
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = (
        f"If you control more creatures than an opponent, this has {CardSpecialType.SNEAKY.value} this turn."
    )
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        if len(game.current_player.cards_laid_out) > len(game.opponent.cards_laid_out):
            if CardSpecialType.SNEAKY not in self.special_types:
                self.special_types.append(CardSpecialType.SNEAKY)
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} has {CardSpecialType.SNEAKY.value} this turn."
            )
        else:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} does not have {CardSpecialType.SNEAKY.value} this turn."
            )


class The_pack(Card):
    name: str = "The Pack"
    strength: int = 4
    special_types: list[CardSpecialType] = [
        CardSpecialType.HUNTER,
        CardSpecialType.TOUGH,
    ]
    description: str = (
        f"While this creature is exhausted, it has {CardSpecialType.SNEAKY.value}."
    )
    set: CardSet = CardSet.PROMO_CARDS

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if self.tough_charges == 0 and CardSpecialType.SNEAKY not in self.special_types:
            self.special_types.append(CardSpecialType.SNEAKY)
            game.log.append(
                f"{game.current_player.name}'s {self.name} has {CardSpecialType.SNEAKY.value}."
            )


class Tiger_squirrel(Card):
    name: str = "Tiger Squirrel"
    strength: int = 3
    special_types: list[CardSpecialType] = [CardSpecialType.SNEAKY]
    action_type: CardActionType = CardActionType.PLAY
    action_description: str = (
        "Defeat an enemy creature with power 7 or more of your choice."
    )
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_tiger_squirrel_action(self)


class Turbo_bug(Card):
    name: str = "Turbo Bug"
    strength: int = 4
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "The opponent loses all life except one."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        lost_life = game.lose_life(
            1 - game.turn,
            game.opponent.number_of_lives - 1,
            auto_end_after_attack=True,
        )
        if lost_life > 0:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} attacks {game.opponent.name} for {lost_life} life."
            )
        else:
            game.log.append(
                f"{game.current_player.name}'s {game.current_player.cards_laid_out[0].name} attacks {game.opponent.name}, but they cannot lose life."
            )


class Turf_the_surfer(Card):
    name: str = "Turf the Surfer"
    strength: int = 8
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Choose a creature. It cannot block this turn."
    set: CardSet = CardSet.NEW_SERVANTS

    def trigger_action(self, game: Game) -> None:
        game.resolve_turf_the_surfer_action(self)


class Tusked_extorter(Card):
    name: str = "Tusked Extorter"
    strength: int = 8
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "The opponent discards a card from their hand."
    set: CardSet = CardSet.FIRST_CONTACT

    def trigger_action(self, game: Game) -> None:
        game.resolve_tusked_extorter_action(self)


class Unigon(Card):
    name: str = "Unigon"
    strength: int = 9
    special_types: list[CardSpecialType] = []
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "If your hand is empty, you win the game."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        if len(game.current_player.hand) == 0:
            game.game_state = GameState.GAME_OVER
            game.winner = game.current_player
            game.log.append(f"{game.current_player.name} wins the game with Unigon.")
        else:
            game.log.append(
                f"{game.current_player.name}'s hand is not empty, so Unigon does not win the game."
            )


class Urchin_hurler(Card):
    name: str = "Urchin Hurler"
    strength: int = 5
    special_types: list[CardSpecialType] = [CardSpecialType.HUNTER]
    description: str = "Other allied creatures have +2 power while it is your turn."
    set: CardSet = CardSet.FIRST_CONTACT

    def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
        if game.current_player is not owner:
            return
        for card in owner.cards_laid_out:
            if card is not self:
                card.strength += 2


# class Watts_dog(Card):
#     name: str = "Watts Dog"
#     strength: int = 5
#     special_types: list[CardSpecialType] = [CardSpecialType.FRENZY]
#     description: str = "Can only be blocked by creatures with no keywords."
#     set: CardSet = CardSet.PROMO_CARDS


class Wheatl_e(Card):
    name: str = "Wheatle"
    strength: int = 6
    special_types: list[CardSpecialType] = [CardSpecialType.FRENZY, CardSpecialType.TOUGH]
    action_type: CardActionType = CardActionType.ATTACK
    action_description: str = "Choose a number. An opponent gives you all cards from their hand with power equal to the chosen number that number. Put them into your hand."
    set: CardSet = CardSet.PROMO_CARDS

    def trigger_action(self, game: Game) -> None:
        game.resolve_wheatle_action(self)


# class Wolfman_steve(Card):
#     name: str = "Wolfman Steve"
#     strength: int = 8
#     special_types: list[CardSpecialType] = []
#     description: str = "Opponent cannot play cards with power 4 or less from their hand."
#     set: CardSet = CardSet.PROMO_CARDS

#     def apply_ongoing_effect(self, game: Game, owner, opponent) -> None:
#         opponent.cannot_play_cards_with_power_4_or_less_from_hand = True
