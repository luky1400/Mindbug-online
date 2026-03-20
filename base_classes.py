from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any, Iterable, Optional

from enums import CardActionType, CardSpecialType, GameState


@dataclass
class Card:
    name: Optional[str] = None # TODO - remove Optional?
    strength: Optional[int] = None # TODO - remove Optional?
    description: Optional[str] = None
    special_types: list[CardSpecialType] = field(default_factory=list) # TODO - rename to keywords
    tough_charges: int = 0
    action_type: Optional[CardActionType] = None
    action_description: Optional[str] = None
    set: Optional[str] = None # TODO - remove Optional?
    cannot_block: bool = False
    cannot_attack: bool = False
    min_blocker_strength: Optional[int] = None
    base_strength: int = field(init=False)
    base_special_types: list[CardSpecialType] = field(init=False) # TODO - rename to base_keywords
    base_cannot_block: bool = field(init=False)
    base_cannot_attack: bool = field(init=False)

    def __post_init__(self) -> None:
        cls = type(self)

        if self.name is None:
            self.name = getattr(cls, "name", None)
        if self.strength is None:
            self.strength = getattr(cls, "strength", None)
        if self.description is None:
            self.description = getattr(cls, "description", None)
        if not self.special_types and hasattr(cls, "special_types"):
            self.special_types = list(getattr(cls, "special_types"))
        if self.action_type is None:
            self.action_type = getattr(cls, "action_type", None)
        if self.action_description is None:
            self.action_description = getattr(cls, "action_description", None)
        if self.set is None:
            self.set = getattr(cls, "set", None)
        if self.min_blocker_strength is None:
            self.min_blocker_strength = getattr(cls, "min_blocker_strength", None)
        if self.tough_charges == 0 and CardSpecialType.TOUGH in self.special_types:
            self.tough_charges = 1
        if self.cannot_block is None:
            self.cannot_block = getattr(cls, "cannot_block", False)

        if self.name is None or self.strength is None:
            raise ValueError("Card requires name and strength.")
        self.base_strength = self.strength
        self.base_special_types = list(self.special_types)
        self.base_cannot_block = self.cannot_block
        self.base_cannot_attack = self.cannot_attack

    def clone(self) -> "Card":
        return type(self)(
            name=self.name,
            strength=self.strength,
            description=self.description,
            special_types=list(self.special_types),
            tough_charges=1 if CardSpecialType.TOUGH in self.special_types else 0,
            action_type=self.action_type,
            action_description=self.action_description,
            set=self.set,
            cannot_block=self.cannot_block,
            min_blocker_strength=self.min_blocker_strength,
        )

    def short_label(self) -> str:
        parts = [f"{self.name} [{self.strength}]"]
        tags = []
        for tag in self.special_types:
            tags.append(tag.value)
        # Render tough_charges if TOUGH is present
        if any(tag == CardSpecialType.TOUGH for tag in self.special_types):
            parts[-1] += f" | tough:{self.tough_charges}"
        label = " ".join(parts)
        # Render tags as <...> if any
        if tags:
            label += f" <{','.join(tags)}>"
        # Render action_type and action_description if action_type present
        if self.action_type is not None:
            label += f" | {self.action_type.value}"
            if self.action_description:
                label += f": {self.action_description}"
        return label

    def trigger_action(self, game: Game) -> None:
        game.log.append(f"{self.name} has no action.")

    def apply_ongoing_effect(self, game: "Game", owner: "Player", opponent: "Player") -> None:
        return

class Deck:
    def __init__(self, cards: Iterable[Card]):
        self.cards: list[Card] = list(cards)
        self.shuffle()

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self, amount: int = 1) -> list[Card]:
        pulled: list[Card] = []
        for _ in range(amount):
            if not self.cards:
                break
            pulled.append(self.cards.pop())
        return pulled

    def __len__(self) -> int:
        return len(self.cards)

    def __getitem__(self, index: int) -> Card:
        return self.cards[index]

    def clear(self) -> None:
        self.cards = []


class DrawPile(Deck):

    def add(self, card: Card) -> None:
        self.cards.append(card)

    def add_multiple(self, cards: list[Card]) -> None:
        self.cards.extend(cards)

    def remove(self, card: Card) -> None:
        self.cards.remove(card)

    def remove_multiple(self, cards: list[Card]) -> None:
        for card in cards:
            self.remove(card)


@dataclass
class Player:
    name: str
    number_of_lives: int = 3
    draw_pile: DrawPile = field(default_factory=lambda: DrawPile([]))
    discard_pile: list[Card] = field(default_factory=list) # TODO - create obejct DiscardPile?
    hand: list[Card] = field(default_factory=list)
    cards_laid_out: list[Card] = field(default_factory=list)
    mindbugs_remaining: int = 2
    cannot_activate_play_effects: bool = False
    cannot_block_with_creatures_with_power_4_or_less: bool = False
    cannot_block_with_creatures_with_highest_power: bool = False
    cannot_attack_with_creatures_with_lowest_power: bool = False

    def draw(self, amount: int = 1) -> None:
        self.hand.extend(self.draw_pile.draw(amount))

    def play_from_hand(self, hand_index: int) -> Card:
        if hand_index < 0 or hand_index >= len(self.hand):
            raise ValueError("Invalid hand index.")
        return self.hand.pop(hand_index)

    def lose_life(self, amount: int = 1) -> None:
        self.number_of_lives = max(0, self.number_of_lives - amount)

    def move_to_discard(self, card: Card) -> None:
        self.discard_pile.append(card)


class Game:
    def __init__(self, player_names: list[str], starting_lives: int = 5, starting_hand_size: int = 5, starting_draw_pile_size: int = 5, players_start_with_mindbugs: int = 2):
        # TODO - Later implement for 4 players
        if len(player_names) != 2:
            raise ValueError("Mindbug supports exactly 2 players.")
        self.players: list[Player] = [Player(name=n) for n in player_names]
        self.turn: int = 0
        self.game_state: GameState = GameState.START_TURN
        self.starting_lives = starting_lives
        self.starting_hand_size = starting_hand_size
        self.starting_draw_pile_size = starting_draw_pile_size
        self.players_start_with_mindbugs: int = players_start_with_mindbugs
        self.winner: Optional[Player] = None
        self.log: list[str] = []
        self._attacks_this_turn: dict[int, int] = {}
        self.number_of_players = len(player_names)
        self.number_of_cards_in_game = (self.starting_draw_pile_size + self.starting_hand_size) * self.number_of_players

    @property
    def current_player(self) -> Player:
        return self.players[self.turn]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.turn]

    def _select_cards_for_game(self, card_pool: list[Card]) -> list[Card]:
        if len(card_pool) < self.number_of_cards_in_game:
            raise ValueError("Card pool does not contain enough cards for a game.")
        selected_cards = random.sample(card_pool, self.number_of_cards_in_game)
        game_cards = [card.clone() for card in selected_cards]
        return game_cards

    def start_game(self, card_pool: list[Card]) -> None:
        game_cards = self._select_cards_for_game(card_pool)

        for player_index, player in enumerate(self.players):
            player_cards = game_cards[player_index::self.number_of_players] # distribute cards evenly among players

            player.number_of_lives = self.starting_lives
            player.hand = []
            player.draw_pile = DrawPile(player_cards)
            player.discard_pile = []
            player.cards_laid_out = []
            player.mindbugs_remaining = self.players_start_with_mindbugs
            player.draw(amount=self.starting_hand_size)

        self.turn = 0
        self.game_state = GameState.ACTIVE
        self.winner = None
        self.log = ["Game started."]
        self._attacks_this_turn = {}
        self._recalculate_ongoing_effects()

    # TODO - refactor - do not return boolean, return None
    # NOTE - card is optional, if not provided, play card from hand - TODO - refactor this
    def play_card(self, hand_index: Optional[int] = None, card: Optional[Card] = None, use_opponent_mindbug: bool = False) -> bool:
        self._ensure_active()
        self._recalculate_ongoing_effects()
        actor = self.current_player
        opponent = self.opponent
        if card is None and hand_index is not None:
            card = actor.play_from_hand(hand_index)

        if use_opponent_mindbug:
            if opponent.mindbugs_remaining <= 0:
                actor.hand.insert(hand_index, card)
                raise ValueError(f"{opponent.name} has no mindbug left.")
            opponent.mindbugs_remaining -= 1
            opponent.cards_laid_out.append(card)
            self._recalculate_ongoing_effects()
            self.log.append(f"{opponent.name} uses Mindbug and steals {card.name}.")
            # If a stolen card has a PLAY action, resolve it for the stealing player.
            if card.action_type == CardActionType.PLAY and not opponent.cannot_activate_play_effects:
                original_turn = self.turn
                self.turn = 1 - self.turn
                try:
                    card.trigger_action(self)
                finally:
                    self.turn = original_turn
                self._recalculate_ongoing_effects()
            self._check_game_over()
            actor.draw(1)
            return True
        else:
            actor.cards_laid_out.append(card)
            self._recalculate_ongoing_effects()
            self.log.append(f"{actor.name} plays {card.name}.")
            # Trigger action if card has a PLAY action type and the actor is allowed to activate it.
            if card.action_type == CardActionType.PLAY and not actor.cannot_activate_play_effects:
                card.trigger_action(self)
                self._recalculate_ongoing_effects()

        self._check_game_over()
        actor.draw(1)
        return False

    # TODO - do not put defender_index as argument to attack function, instead create defend function that takes attacker and defender and is used inside attack function
    # In defend function - implement - can_block_attack for all cards laid out on the battlefield - then let defender decide only from cards that can block, if cards_can_block == empty - loose life directly.
    def attack(self, attacker_index: int, defender_index: Optional[int] = None, hunter_target_override: bool = True) -> None:
        self._ensure_active()
        self._recalculate_ongoing_effects()
        attacker_owner = self.current_player
        defender_owner = self.opponent

        if attacker_index < 0 or attacker_index >= len(attacker_owner.cards_laid_out):
            raise ValueError("Invalid attacker index.")

        if len(attacker_owner.cards_laid_out) == 0:
            raise ValueError("No cards laid out to attack.")

        attacker = attacker_owner.cards_laid_out[attacker_index]
        if attacker.cannot_attack:
            raise ValueError(f"{attacker.name} cannot attack right now.")
        attacks_used = self._attacks_this_turn.get(id(attacker), 0)
        max_attacks = 2 if CardSpecialType.FRENZY in attacker.special_types else 1
        if attacks_used >= max_attacks:
            raise ValueError(f"{attacker.name} cannot attack more than {max_attacks} times this turn.")
        self._attacks_this_turn[id(attacker)] = attacks_used + 1

        # Trigger action if attacker has an action type
        if attacker.action_type == CardActionType.ATTACK:
            attacker.trigger_action(self)
            # ATTACK action can remove attacker before combat resolution (e.g. Snail Hydra attacks and destroys Explosive Toad, which then destroys Snail Hydra).
            if attacker not in attacker_owner.cards_laid_out:
                self.log.append(
                    f"{attacker_owner.name}'s {attacker.name} is no longer on the battlefield. Attack is cancelled."
                )
                return

        if defender_index is None:
            defender_owner.lose_life(1)
            self.log.append(f"{attacker_owner.name}'s {attacker.name} attacks directly for 1 life.")
            self._check_game_over()
            return

        if defender_index < 0 or defender_index >= len(defender_owner.cards_laid_out):
            raise ValueError("Invalid defender index.")
        defender = defender_owner.cards_laid_out[defender_index]
        attacker_has_hunter = (
            hunter_target_override and CardSpecialType.HUNTER in attacker.special_types
        )
        if not attacker_has_hunter:
            if defender.cannot_block:
                raise ValueError(f"{defender.name} cannot block right now.")
            if (
                CardSpecialType.SNEAKY in attacker.special_types
                and CardSpecialType.SNEAKY not in defender.special_types
            ):
                raise ValueError(
                    f"{defender.name} cannot block {attacker.name} because only SNEAKY creatures can defend against SNEAKY attackers."
                )
            if (
                attacker.min_blocker_strength is not None
                and defender.strength < attacker.min_blocker_strength
            ):
                raise ValueError(
                    f"{defender.name} is too weak to block {attacker.name}."
                )

        attacker_defeated = self._is_defeated(attacker, defender)
        defender_defeated = self._is_defeated(defender, attacker)

        if attacker_defeated:
            self._destroy_creature(attacker_owner, attacker)
        if defender_defeated:
            self._destroy_creature(defender_owner, defender)

        self.log.append(
            f"{attacker_owner.name}'s {attacker.name} attacks {defender_owner.name}'s {defender.name}."
        )

    def _is_eligible_defender(
        self,
        attacker: Card,
        defender: Card,
        hunter_target_override: bool = True,
    ) -> bool:
        if hunter_target_override and CardSpecialType.HUNTER in attacker.special_types:
            return True
        if defender.cannot_block:
            return False
        if (
            CardSpecialType.SNEAKY in attacker.special_types
            and CardSpecialType.SNEAKY not in defender.special_types
        ):
            return False
        if (
            attacker.min_blocker_strength is not None
            and defender.strength < attacker.min_blocker_strength
        ):
            return False
        return True

    def get_eligible_defender_indices(
        self,
        attacker_index: int,
        hunter_target_override: bool = True,
    ) -> list[int]:
        self._ensure_active()
        self._recalculate_ongoing_effects()
        attacker_owner = self.current_player
        defender_owner = self.opponent

        if attacker_index < 0 or attacker_index >= len(attacker_owner.cards_laid_out):
            raise ValueError("Invalid attacker index.")

        attacker = attacker_owner.cards_laid_out[attacker_index]
        return [
            index
            for index, defender in enumerate(defender_owner.cards_laid_out)
            if self._is_eligible_defender(
                attacker, defender, hunter_target_override=hunter_target_override
            )
        ]

    def end_turn(self) -> None:
        self._ensure_active()
        self.turn = 1 - self.turn
        self._attacks_this_turn = {}
        self._recalculate_ongoing_effects()
        self.game_state = GameState.START_TURN
        self.log.append(f"Turn passes to {self.current_player.name}.")

    def get_state(self) -> dict[str, Any]:
        turn_player = self.current_player
        players_state = [self._serialize_player(p) for p in self.players]
        indexed_turn_hand = ", ".join(f"{index}: {card.short_label()}" for index, card in enumerate(turn_player.hand))
        for player_state in players_state:
            if player_state["name"] == turn_player.name:
                # Backward compatibility: older UIs only render `hand_count`.
                player_state["hand_count"] = f"{len(turn_player.hand)} ({indexed_turn_hand if indexed_turn_hand else '-'})"
                break
        return {
            "game_state": self.game_state.value,
            "turn_player": turn_player.name,
            "winner": None if not self.winner else self.winner.name,
            "turn_hand": [card.short_label() for card in turn_player.hand],
            "players": players_state,
            "log": list(self.log[-10:]),
        }

    def _serialize_player(self, player: Player) -> dict[str, Any]:
        return {
            "name": player.name,
            "lives": player.number_of_lives,
            "mindbugs_remaining": player.mindbugs_remaining,
            "hand_count": len(player.hand),
            "hand": [card.short_label() for card in player.hand],
            "battlefield": [c.short_label() for c in player.cards_laid_out],
            "discard_count": len(player.discard_pile),
            "discard": [card.short_label() for card in player.discard_pile],
            "draw_count": len(player.draw_pile.cards),
        }

    def _destroy_creature(self, owner: Player, creature: Card, ignore_tough: bool = False) -> None:
        if CardSpecialType.TOUGH in creature.special_types and creature.tough_charges > 0 and not ignore_tough:
            creature.tough_charges -= 1
            self.log.append(f"{creature.name} survives due to TOUGH.")
            return
        owner.cards_laid_out.remove(creature)
        owner.move_to_discard(creature)
        self.log.append(f"{owner.name}'s {creature.name} is defeated.")
        
        # Trigger action if creature has a DEFEATED action type
        if creature.action_type == CardActionType.DEFEATED:
            creature.trigger_action(self)
            self.log.append(f"{owner.name}'s {creature.name} is defeated and triggers its DEFEATED action.")
        
        self._recalculate_ongoing_effects()
        self._check_game_over()

    def _is_defeated(self, defender: Card, attacker: Card) -> bool:
        if CardSpecialType.POISONOUS in attacker.special_types:
            return True
        return attacker.strength >= defender.strength

    def _check_game_over(self) -> None:
        for player in self.players:
            if player.number_of_lives <= 0 or (len(player.cards_laid_out) == 0 and len(player.hand) == 0 and len(player.draw_pile.cards) == 0):
                self.game_state = GameState.GAME_OVER
                self.winner = self.players[0] if self.players[1] == player else self.players[1]
                self.log.append(f"{self.winner.name} wins.")

    def _ensure_active(self) -> None:
        if self.game_state == GameState.GAME_OVER:
            raise ValueError("Game is already over.")

    def _recalculate_ongoing_effects(self) -> None:
        for player in self.players:
            player.cannot_activate_play_effects = False
            player.cannot_block_with_creatures_with_power_4_or_less = False
            player.cannot_block_with_creatures_with_highest_power = False
            player.cannot_attack_with_creatures_with_lowest_power = False
            for card in player.cards_laid_out:
                card.strength = card.base_strength
                card.special_types = list(card.base_special_types)
                card.cannot_block = card.base_cannot_block
                card.cannot_attack = card.base_cannot_attack

        for owner_idx, owner in enumerate(self.players):
            opponent = self.players[1 - owner_idx]
            for card in owner.cards_laid_out:
                card.apply_ongoing_effect(self, owner, opponent)

        for player in self.players:
            if player.cannot_block_with_creatures_with_power_4_or_less:
                for card in player.cards_laid_out:
                    if card.strength <= 4:
                        card.cannot_block = True

            if player.cannot_block_with_creatures_with_highest_power and player.cards_laid_out:
                highest_power = max(card.strength for card in player.cards_laid_out)
                for card in player.cards_laid_out:
                    if card.strength == highest_power:
                        card.cannot_block = True

            if player.cannot_attack_with_creatures_with_lowest_power and player.cards_laid_out:
                lowest_power = min(card.strength for card in player.cards_laid_out)
                for card in player.cards_laid_out:
                    if card.strength == lowest_power:
                        card.cannot_attack = True