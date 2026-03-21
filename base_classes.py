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


@dataclass
class PendingMindbugDecision:
    acting_player_index: int
    responding_player_index: int
    card: Card


class Game:
    def __init__(
        self,
        player_names: list[str],
        starting_lives: int = 3,
        starting_hand_size: int = 5,
        starting_draw_pile_size: int = 5,
        players_start_with_mindbugs: int = 2,
        await_mindbug_response: bool = False,
        enforce_turn_action_limit: bool = False,
        auto_end_turn_after_successful_play: bool = False,
    ):
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
        self._turn_action_taken: bool = False
        self._pending_frenzy_attacker_id: int | None = None
        self._pending_mindbug_decision: PendingMindbugDecision | None = None
        self.number_of_players = len(player_names)
        self.number_of_cards_in_game = (self.starting_draw_pile_size + self.starting_hand_size) * self.number_of_players
        self.await_mindbug_response = await_mindbug_response
        self.enforce_turn_action_limit = enforce_turn_action_limit
        self.auto_end_turn_after_successful_play = auto_end_turn_after_successful_play

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
        self._turn_action_taken = False
        self._pending_frenzy_attacker_id = None
        self._pending_mindbug_decision = None
        self._recalculate_ongoing_effects()

    def play_card(
        self,
        hand_index: Optional[int] = None,
        card: Optional[Card] = None,
    ) -> None:
        """
        Plays a card.
        If card is not provided, plays a card from the hand.
        If opponent has Mindbug remaining and we are awaiting mindbug response, we await mindbug response from opponent.
        If opponent declines to use Mindbug, we play the card and end the turn.
        If opponent uses Mindbug, we play the card and end the turn.

        Args:
            hand_index: Index of the card to play from the hand.
            card: Card to play. If not provided, plays a card from the hand.
        """
        self._ensure_active()
        self._ensure_no_pending_resolution()
        if self.enforce_turn_action_limit and self._turn_action_taken:
            raise ValueError("You already took your action this turn.")
        self._recalculate_ongoing_effects()
        actor = self.current_player
        opponent = self.opponent
        if card is None and hand_index is not None:
            card = actor.play_from_hand(hand_index)
        if card is None:
            raise ValueError("No card was selected to play.")

        self.log.append(f"{actor.name} plays {card.name}.")
        if opponent.mindbugs_remaining > 0 and self.await_mindbug_response:
            self._pending_mindbug_decision = PendingMindbugDecision(
                acting_player_index=self.turn,
                responding_player_index=1 - self.turn,
                card=card,
            )
            self.game_state = GameState.AWAITING_MINDBUG
            self.log.append(f"Waiting for {opponent.name} to decide whether to use Mindbug.")
            return

        self._finalize_played_card(owner_index=self.turn, card=card)
        if opponent.mindbugs_remaining > 0:
            self.log.append(f"{opponent.name} declines to use Mindbug.")
        else:
            self.log.append(f"{opponent.name} has no Mindbug left.")
        self._auto_end_turn_after_play_if_needed()

    def respond_to_mindbug(self, use_mindbug: bool) -> None:
        self._ensure_active() # redundant?
        if self._pending_mindbug_decision is None:
            raise ValueError("There is no pending Mindbug decision.")

        pending = self._pending_mindbug_decision
        actor_index = pending.acting_player_index
        responder_index = pending.responding_player_index
        actor = self.players[actor_index]
        responder = self.players[responder_index]
        card = pending.card

        self._pending_mindbug_decision = None
        self.game_state = GameState.ACTIVE

        if use_mindbug:
            if responder.mindbugs_remaining <= 0:
                self._finalize_played_card(owner_index=actor_index, card=card)
                self.log.append(f"{responder.name} tried to use Mindbug but has none left.")
                return

            responder.mindbugs_remaining -= 1
            self.log.append(f"{responder.name} uses Mindbug and steals {card.name}.")
            self._finalize_played_card(
                owner_index=responder_index,
                card=card,
                draw_for_player_index=actor_index,
                consume_turn_action=False,
            )
            return

        self.log.append(f"{responder.name} declines to use Mindbug.")
        self._finalize_played_card(owner_index=actor_index, card=card)
        self._auto_end_turn_after_play_if_needed()

    # TODO - do not put defender_index as argument to attack function, instead create defend function that takes attacker and defender and is used inside attack function
    # In defend function - implement - can_block_attack for all cards laid out on the battlefield - then let defender decide only from cards that can block, if cards_can_block == empty - loose life directly.
    def attack(self, attacker_index: int, defender_index: Optional[int] = None, hunter_target_override: bool = True) -> None:
        self._ensure_active()
        self._ensure_no_pending_resolution()
        self._recalculate_ongoing_effects()
        attacker_owner = self.current_player
        defender_owner = self.opponent
        is_resolving_frenzy_attack = self._pending_frenzy_attacker_id is not None

        if self.enforce_turn_action_limit and self._turn_action_taken and not is_resolving_frenzy_attack:
            raise ValueError("You already took your action this turn.")

        if attacker_index < 0 or attacker_index >= len(attacker_owner.cards_laid_out):
            raise ValueError("Invalid attacker index.")

        if len(attacker_owner.cards_laid_out) == 0:
            raise ValueError("No cards laid out to attack.")

        attacker = attacker_owner.cards_laid_out[attacker_index]
        if is_resolving_frenzy_attack and id(attacker) != self._pending_frenzy_attacker_id:
            raise ValueError("You must use the same FRENZY creature for the bonus attack.")
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
                self._turn_action_taken = True
                self._pending_frenzy_attacker_id = None
                self.log.append(
                    f"{attacker_owner.name}'s {attacker.name} is no longer on the battlefield. Attack is cancelled."
                )
                return

        if defender_index is None:
            defender_owner.lose_life(1)
            self.log.append(f"{attacker_owner.name}'s {attacker.name} attacks directly for 1 life.")
            self._check_game_over()
            self._finalize_attack_action(attacker_owner, attacker)
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
        self._finalize_attack_action(attacker_owner, attacker)

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
        self._ensure_no_pending_resolution()
        self.turn = 1 - self.turn
        self._attacks_this_turn = {}
        self._turn_action_taken = False
        self._pending_frenzy_attacker_id = None
        self._recalculate_ongoing_effects()
        self.game_state = GameState.START_TURN
        self.log.append(f"Turn passes to {self.current_player.name}.")

    def get_state(self, viewer_index: Optional[int] = None) -> dict[str, Any]:
        if viewer_index is not None:
            return self._build_player_view(viewer_index)

        turn_player = self.current_player
        players_state = [self._serialize_player(index) for index in range(len(self.players))]
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

    def _serialize_player(self, player_index: int, include_hand: bool = True) -> dict[str, Any]:
        player = self.players[player_index]
        return {
            "player_index": player_index,
            "name": player.name,
            "lives": player.number_of_lives,
            "mindbugs_remaining": player.mindbugs_remaining,
            "hand_count": len(player.hand),
            "hand": [card.short_label() for card in player.hand] if include_hand else [],
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

    def _ensure_no_pending_resolution(self) -> None:
        if self._pending_mindbug_decision is not None:
            responder = self.players[self._pending_mindbug_decision.responding_player_index]
            raise ValueError(f"Waiting for {responder.name} to decide whether to use Mindbug.")

    def _finalize_played_card(
        self,
        owner_index: int,
        card: Card,
        draw_for_player_index: Optional[int] = None,
        consume_turn_action: bool = True,
    ) -> None:
        owner = self.players[owner_index]
        owner.cards_laid_out.append(card)
        self._recalculate_ongoing_effects()
        if card.action_type == CardActionType.PLAY and not owner.cannot_activate_play_effects:
            original_turn = self.turn
            self.turn = owner_index
            try:
                card.trigger_action(self)
            finally:
                self.turn = original_turn
            self._recalculate_ongoing_effects()

        self._check_game_over()
        draw_owner_index = owner_index if draw_for_player_index is None else draw_for_player_index
        self.players[draw_owner_index].draw(1)
        if self.enforce_turn_action_limit and consume_turn_action:
            self._turn_action_taken = True
            self._pending_frenzy_attacker_id = None

    def _finalize_attack_action(self, attacker_owner: Player, attacker: Card) -> None:
        if not self.enforce_turn_action_limit:
            self._pending_frenzy_attacker_id = None
            return

        self._turn_action_taken = True
        if (
            CardSpecialType.FRENZY in attacker.special_types
            and attacker in attacker_owner.cards_laid_out
            and self._attacks_this_turn.get(id(attacker), 0) == 1
            and self.game_state != GameState.GAME_OVER
        ):
            self._pending_frenzy_attacker_id = id(attacker)
            self.log.append(f"{attacker.name} may attack one more time this turn due to FRENZY.")
            return

        self._pending_frenzy_attacker_id = None

    def _build_player_view(self, viewer_index: int) -> dict[str, Any]:
        viewer = self.players[viewer_index]
        opponent_index = 1 - viewer_index
        opponent = self.players[opponent_index]
        pending_mindbug = None
        if self._pending_mindbug_decision is not None:
            pending_mindbug = {
                "acting_player_name": self.players[self._pending_mindbug_decision.acting_player_index].name,
                "responding_player_name": self.players[self._pending_mindbug_decision.responding_player_index].name,
                "card_label": self._pending_mindbug_decision.card.short_label(),
                "response_required_from_viewer": self._pending_mindbug_decision.responding_player_index == viewer_index,
            }

        return {
            "game_state": self.game_state.value,
            "room_status": self.game_state.value,
            "turn_player": self.current_player.name,
            "winner": None if not self.winner else self.winner.name,
            "viewer_player_name": viewer.name,
            "viewer_player_index": viewer_index,
            "opponent_player_name": opponent.name,
            "is_viewer_turn": self.turn == viewer_index,
            "viewer": self._serialize_player(viewer_index, include_hand=True),
            "opponent": self._serialize_player(opponent_index, include_hand=False),
            "log": list(self.log[-10:]),
            "pending_mindbug": pending_mindbug,
            "pending_frenzy_attacker_index": self._get_pending_frenzy_attacker_index(viewer_index),
        }

    def _auto_end_turn_after_play_if_needed(self) -> None:
        if not self.auto_end_turn_after_successful_play:
            return
        if self.game_state == GameState.GAME_OVER:
            return
        self.end_turn()

    def _get_pending_frenzy_attacker_index(self, viewer_index: int) -> int | None:
        if self._pending_frenzy_attacker_id is None or self.turn != viewer_index:
            return None

        for index, card in enumerate(self.players[viewer_index].cards_laid_out):
            if id(card) == self._pending_frenzy_attacker_id:
                return index
        return None

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