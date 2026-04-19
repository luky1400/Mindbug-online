from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any, Iterable, Optional

from enums import (
    CardActionType,
    CardSet,
    CardSpecialType,
    GameState,
    OngoingEffectPriority,
)


@dataclass
class Card:
    name: Optional[str] = None  # TODO - remove Optional?
    strength: Optional[int] = None  # TODO - remove Optional?
    description: Optional[str] = None
    special_types: list[CardSpecialType] = field(
        default_factory=list
    )  # TODO - rename to keywords
    tough_charges: int = 0
    action_type: Optional[CardActionType] = None
    action_description: Optional[str] = None
    set: Optional[CardSet] = None  # TODO - remove Optional?
    cannot_block: bool = False
    cannot_attack: bool = False
    min_blocker_strength: Optional[int] = None
    requires_blocker_with_no_special_types: Optional[bool] = None
    base_strength: int = field(init=False)
    base_special_types: list[CardSpecialType] = field(
        init=False
    )  # TODO - rename to base_keywords
    base_cannot_block: bool = field(init=False)
    base_cannot_attack: bool = field(init=False)
    temporary_cannot_block_until_turn_end: bool = False
    apply_ongoing_effect_priority: OngoingEffectPriority = OngoingEffectPriority.NORMAL

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
        if self.requires_blocker_with_no_special_types is None:
            self.requires_blocker_with_no_special_types = getattr(
                cls, "requires_blocker_with_no_special_types", False
            )
        # Using cls.__dict__ (not getattr) to only match direct definitions on the subclass, not inherited ones.
        if "apply_ongoing_effect_priority" in cls.__dict__:
            self.apply_ongoing_effect_priority = cls.__dict__[
                "apply_ongoing_effect_priority"
            ]
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
            requires_blocker_with_no_special_types=self.requires_blocker_with_no_special_types,
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

    def apply_ongoing_effect(
        self, game: "Game", owner: "Player", opponent: "Player"
    ) -> None:
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
    discard_pile: list[Card] = field(
        default_factory=list
    )  # TODO - create obejct DiscardPile?
    hand: list[Card] = field(default_factory=list)
    cards_laid_out: list[Card] = field(default_factory=list)
    mindbugs_remaining: int = 2
    cannot_activate_play_effects: bool = False
    life_loss_before_using_mindbug: int = 0
    cannot_lose_life: bool = False
    cannot_play_cards_with_power_4_or_less_from_hand: bool = False

    def draw(self, amount: int = 1) -> None:
        self.hand.extend(self.draw_pile.draw(amount))

    def play_from_hand(self, hand_index: int) -> Card:
        if hand_index < 0 or hand_index >= len(self.hand):
            raise ValueError("Invalid hand index.")
        return self.hand.pop(hand_index)

    # NOTE - not used, lose_life method on Game is used instead
    def lose_life(self, amount: int = 1) -> int:
        if amount <= 0 or self.cannot_lose_life:
            return 0
        previous_life = self.number_of_lives
        self.number_of_lives = max(0, self.number_of_lives - amount)
        return previous_life - self.number_of_lives

    def move_to_discard(self, card: Card) -> None:
        if CardSpecialType.TOUGH in card.special_types:
            card.tough_charges = 1
        self.discard_pile.append(card)


@dataclass
class PendingMindbugDecision:
    acting_player_index: int
    responding_player_index: int
    card: Card


@dataclass
class PendingDefenseDecision:
    attacking_player_index: int
    defending_player_index: int
    attacker: Card


@dataclass
class PendingCardActionChoice:
    action_key: str
    source_card: Card
    responding_player_index: int
    selection_owner_index: int
    selection_zone: str
    eligible_indices: list[int]
    min_choices: int
    max_choices: int
    option_labels: list[str] | None = None
    staged_card: Card | None = None
    draw_up_to_hand_limit_after_resolution: bool = False
    auto_end_after_play: bool = False
    auto_end_after_attack: bool = False


@dataclass
class PendingAttackContinuation:
    attacker: Card
    attacker_owner_index: int
    defender: Optional[Card]
    defender_owner_index: int


@dataclass
class DefeatedCreatureEntry:
    owner_index: int
    creature: Card
    owner_name: str
    card_label: str  # snapshot at time of death


@dataclass
class PendingDefeatedOrdering:
    responding_player_index: int
    entries: list[DefeatedCreatureEntry]


@dataclass
class PendingCombatFinalization:
    attacker: Card
    attacker_owner_index: int


@dataclass
class PendingHyenixTrigger:
    owner_index: int
    card: Card
    auto_end_after_play: bool = False
    auto_end_after_attack: bool = False


@dataclass
class PendingSluggernautFormChoice:
    owner_index: int
    card: Card


class Game:
    def __init__(
        self,
        player_names: list[str],
        starting_lives: int = 3,
        starting_draw_pile_size: int = 10,
        players_start_with_mindbugs: int = 2,
        await_mindbug_response: bool = False,
        enforce_turn_action_limit: bool = False,
        auto_end_turn_after_successful_play: bool = False,
        auto_end_turn_after_resolved_attack: bool = False,
    ):
        if len(player_names) != 2:
            raise ValueError("Mindbug game supports exactly 2 players.")
        self.players: list[Player] = [Player(name=n) for n in player_names]
        self.turn: int = 0
        self.game_state: GameState = GameState.START_TURN
        self.starting_lives = starting_lives
        self.starting_draw_pile_size = starting_draw_pile_size
        self.players_start_with_mindbugs: int = players_start_with_mindbugs
        self.winner: Optional[Player] = None
        self.log: list[str] = []
        self._attacks_this_turn: dict[int, int] = {}
        self._turn_action_taken: bool = False
        self._pending_frenzy_attacker_id: int | None = None
        self._pending_mindbug_decision: PendingMindbugDecision | None = None
        self._pending_defense_decision: PendingDefenseDecision | None = None
        self._pending_card_action_choice: PendingCardActionChoice | None = None
        self._pending_attack_continuation: PendingAttackContinuation | None = None
        self._pending_defeated_ordering: PendingDefeatedOrdering | None = None
        self._defeated_action_queue: list[DefeatedCreatureEntry] = []
        self._pending_combat_finalization: PendingCombatFinalization | None = None
        self._play_is_stolen_by_mindbug: bool = False
        self._pending_hyenix_triggers: list[PendingHyenixTrigger] = []
        self._pending_sluggernaut_form_choices: list[PendingSluggernautFormChoice] = []
        self.number_of_players = len(player_names)
        self.number_of_cards_in_game = (
            self.starting_draw_pile_size * self.number_of_players
        )
        self.await_mindbug_response = await_mindbug_response
        self.enforce_turn_action_limit = enforce_turn_action_limit
        self.auto_end_turn_after_successful_play = auto_end_turn_after_successful_play
        self.auto_end_turn_after_resolved_attack = auto_end_turn_after_resolved_attack
        self.card_pool: list[Card] = []
        self.selected_sets: list[CardSet] = []
        self.unused_pile: list[Card] = []
        self.hand_size_limit = 5

    @property
    def current_player(self) -> Player:
        return self.players[self.turn]

    @property
    def opponent(self) -> Player:
        return self.players[1 - self.turn]

    def _resolve_selected_sets(self, sets: list[CardSet] | None) -> list[CardSet]:
        if sets is not None:
            resolved_sets: list[CardSet] = []
            for card_set in sets:
                if card_set not in resolved_sets:
                    resolved_sets.append(card_set)
            return resolved_sets

        available_sets: list[CardSet] = []
        for card in self.card_pool:
            if card.set is not None and card.set not in available_sets:
                available_sets.append(card.set)
        return available_sets

    def _select_cards_for_game(self) -> list[Card]:
        if len(self.card_pool) < self.number_of_cards_in_game:
            raise ValueError("Card pool does not contain enough cards for a game.")
        selected_cards = random.sample(self.card_pool, self.number_of_cards_in_game)
        selected_names = {card.name for card in selected_cards}
        self.unused_pile = [
            card.clone() for card in self.card_pool if card.name not in selected_names
        ]
        random.shuffle(self.unused_pile)
        return [card.clone() for card in selected_cards]

    def _draw_up_to_hand_limit_if_needed(self, player: Player) -> int:
        cards_drawn = 0
        while (
            len(player.hand) < self.hand_size_limit and len(player.draw_pile.cards) > 0
        ):
            player.draw(1)
            cards_drawn += 1
        return cards_drawn

    def _draw_up_to_hand_limit_for_each_player_if_needed(self) -> None:
        for player in self.players:
            self._draw_up_to_hand_limit_if_needed(player)

    def start_game(self, sets: list[CardSet] | None = None) -> None:
        from cards import get_card_pool

        self.card_pool = get_card_pool(sets=sets)
        self.selected_sets = self._resolve_selected_sets(sets)
        game_cards = self._select_cards_for_game()

        for player_index, player in enumerate(self.players):
            player_cards = game_cards[
                player_index :: self.number_of_players
            ]  # distribute cards evenly among players

            player.number_of_lives = self.starting_lives
            player.hand = []
            player.draw_pile = DrawPile(player_cards)
            player.discard_pile = []
            player.cards_laid_out = []
            player.mindbugs_remaining = self.players_start_with_mindbugs
        self._draw_up_to_hand_limit_for_each_player_if_needed()

        self.turn = random.randrange(self.number_of_players)
        self.game_state = GameState.ACTIVE
        self.winner = None
        self.log = [f"Game started. {self.current_player.name} goes first."]
        self._attacks_this_turn = {}
        self._turn_action_taken = False
        self._pending_frenzy_attacker_id = None
        self._pending_mindbug_decision = None
        self._pending_defense_decision = None
        self._pending_card_action_choice = None
        self._pending_attack_continuation = None
        self._pending_defeated_ordering = None
        self._defeated_action_queue = []
        self._pending_combat_finalization = None
        self._pending_hyenix_triggers = []
        self._pending_sluggernaut_form_choices = []
        self._recalculate_ongoing_effects()

    # NOTe - mabe beter to split: play_card and play_card_from_hand functions?
    def play_card(
        self,
        hand_index: Optional[int] = None,
        card: Optional[Card] = None,
    ) -> None:
        """
        Play a card from hand or from another zone/effect.

        Args:
            hand_index: Index of the card to play from the hand.
            card: Card to play directly. Used for effect-driven plays.
        """
        self._ensure_active()
        self._ensure_no_pending_resolution()
        self._recalculate_ongoing_effects()
        self._ensure_hand_card_play_allowed(hand_index=hand_index, card=card)
        card_to_play, played_from_hand = self._resolve_card_to_play(
            hand_index=hand_index, card=card
        )
        if (
            self.enforce_turn_action_limit
            and self._turn_action_taken
            and played_from_hand
        ):
            raise ValueError("You already took your action this turn.")
        actor = self.current_player

        self.log.append(f"{actor.name} plays {card_to_play.name}.")
        if self._queue_pending_mindbug_decision_if_needed(
            card=card_to_play, played_from_hand=played_from_hand
        ):
            return

        self._finalize_play_without_mindbug(
            owner_index=self.turn,
            card=card_to_play,
            played_from_hand=played_from_hand,
        )

    def respond_to_mindbug(self, use_mindbug: bool) -> None:
        self._ensure_active()  # redundant?
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
                self.log.append(
                    f"{responder.name} tried to use Mindbug but has none left."
                )
                return

            if responder.life_loss_before_using_mindbug > 0:
                lost_life = self.lose_life(
                    responder_index, responder.life_loss_before_using_mindbug
                )
                if lost_life > 0:
                    self.log.append(
                        f"{responder.name} loses {lost_life} life before using Mindbug."
                    )
                else:
                    self.log.append(
                        f"{responder.name} would lose life before using Mindbug, but cannot lose life."
                    )
                self._check_game_over()
                if self.game_state == GameState.GAME_OVER:
                    return

            responder.mindbugs_remaining -= 1
            self.log.append(f"{responder.name} uses Mindbug and steals {card.name}.")
            self._finalize_played_card(
                owner_index=responder_index,
                card=card,
                consume_turn_action=False,
            )
            return

        self.log.append(f"{responder.name} declines to use Mindbug.")
        self._finalize_played_card(owner_index=actor_index, card=card)
        self._auto_end_turn_after_play_if_needed()

    def _resolve_card_to_play(
        self, hand_index: Optional[int], card: Optional[Card]
    ) -> tuple[Card, bool]:
        if card is not None:
            return card, False
        if hand_index is None:
            raise ValueError("No card was selected to play.")

        card_from_hand = self.current_player.play_from_hand(hand_index)
        self._draw_up_to_hand_limit_for_each_player_if_needed()
        return card_from_hand, True

    def _ensure_hand_card_play_allowed(
        self, hand_index: Optional[int], card: Optional[Card]
    ) -> None:
        # Only restrict plays from hand; effect-driven plays (card argument) bypass this check.
        if card is not None or hand_index is None:
            return
        actor = self.current_player
        if hand_index < 0 or hand_index >= len(actor.hand):
            return
        prospective_card = actor.hand[hand_index]
        if (
            actor.cannot_play_cards_with_power_4_or_less_from_hand
            and prospective_card.strength is not None
            and prospective_card.strength <= 4
        ):
            raise ValueError(
                f"{prospective_card.name} cannot be played from hand because the opponent has Wolfman Steve in play."
            )

    def _queue_pending_mindbug_decision_if_needed(
        self, card: Card, played_from_hand: bool
    ) -> bool:
        if not played_from_hand or not self.await_mindbug_response:
            return False

        opponent = self.opponent
        if opponent.mindbugs_remaining <= 0:
            return False

        self._pending_mindbug_decision = PendingMindbugDecision(
            acting_player_index=self.turn,
            responding_player_index=1 - self.turn,
            card=card,
        )
        self.game_state = GameState.AWAITING_MINDBUG
        self.log.append(
            f"Waiting for {opponent.name} to decide whether to use Mindbug."
        )
        return True

    def _finalize_play_without_mindbug(
        self, owner_index: int, card: Card, played_from_hand: bool
    ) -> None:
        opponent = self.players[1 - owner_index]
        self._finalize_played_card(owner_index=owner_index, card=card)
        if played_from_hand:
            if opponent.mindbugs_remaining > 0:
                self.log.append(f"{opponent.name} declines to use Mindbug.")
            else:
                self.log.append(f"{opponent.name} has no Mindbug left.")
        self._auto_end_turn_after_play_if_needed()

    def _set_pending_card_action_choice(
        self,
        action_key: str,
        source_card: Card,
        responding_player_index: int,
        selection_owner_index: int,
        selection_zone: str,
        eligible_indices: list[int],
        min_choices: int,
        max_choices: int,
        option_labels: list[str] | None = None,
        staged_card: Card | None = None,
        draw_up_to_hand_limit_after_resolution: bool = False,
        auto_end_after_play: bool = False,
        auto_end_after_attack: bool = False,
    ) -> None:
        pending = PendingCardActionChoice(
            action_key=action_key,
            source_card=source_card,
            responding_player_index=responding_player_index,
            selection_owner_index=selection_owner_index,
            selection_zone=selection_zone,
            eligible_indices=eligible_indices,
            min_choices=min_choices,
            max_choices=max_choices,
            option_labels=option_labels,
            staged_card=staged_card,
            draw_up_to_hand_limit_after_resolution=draw_up_to_hand_limit_after_resolution,
            auto_end_after_play=auto_end_after_play,
            auto_end_after_attack=auto_end_after_attack,
        )
        auto_selected_indices = self._get_auto_selected_card_action_indices(pending)
        if auto_selected_indices is not None:
            self._resolve_card_action_choice(
                pending, auto_selected_indices, apply_post_resolution_effects=False
            )
            return

        self._pending_card_action_choice = pending
        self.log.append(self._build_pending_card_action_prompt(pending))

    def _get_auto_selected_card_action_indices(
        self, pending: PendingCardActionChoice
    ) -> list[int] | None:
        eligible_count = len(pending.eligible_indices)
        if eligible_count == 0:
            return []
        if pending.min_choices == pending.max_choices == eligible_count:
            return list(pending.eligible_indices)
        if pending.min_choices == pending.max_choices == 1 and eligible_count == 1:
            return [pending.eligible_indices[0]]
        return None

    def _build_pending_card_action_prompt(
        self, pending: PendingCardActionChoice
    ) -> str:
        responder_name = self.players[pending.responding_player_index].name
        if pending.action_key == "brain_fly":
            return f"Waiting for {responder_name} to choose a creature to steal with Brain Fly."
        if pending.action_key == "compost_dragon":
            return f"Waiting for {responder_name} to choose a card to play from the discard pile."
        if pending.action_key == "count_draculeech":
            return f"Waiting for {responder_name} to choose a creature to defeat with Count Draculeech."
        if pending.action_key == "ferret_bomber":
            return f"Waiting for {responder_name} to choose cards to discard for Ferret Bomber."
        if pending.action_key == "explosive_toad":
            return f"Waiting for {responder_name} to choose a creature to defeat with Explosive Toad."
        if pending.action_key == "short_neck_giraffodile":
            return f"Waiting for {responder_name} to choose 2 cards to draw from their discard pile."
        if pending.action_key == "snail_hydra":
            return f"Waiting for {responder_name} to choose a creature to defeat with Snail Hydra."
        if pending.action_key == "grave_robber":
            return f"Waiting for {responder_name} to choose a card to play from the opponent's discard pile."
        if pending.action_key == "harpy_mother":
            return f"Waiting for {responder_name} to choose enemy creatures to take control of with Harpy Mother."
        if pending.action_key == "hyenix":
            return f"Waiting for {responder_name} to choose whether to play Hyenix from their discard pile."
        if pending.action_key == "hungry_hungry_hamster_give":
            return f"Waiting for {responder_name} to choose a card to give away for Hungry Hungry Hamster."
        if pending.action_key == "hungry_hungry_hamster_place":
            return f"Waiting for {responder_name} to choose whether to play the received card or put it into their hand."
        if pending.action_key == "shark_dog":
            return f"Waiting for {responder_name} to choose a creature with power 6 or more to defeat with Shark Dog."
        if pending.action_key == "sluggernaut":
            return f"Waiting for {responder_name} to choose Sluggernaut's new form."
        if pending.action_key == "tiger_squirrel":
            return f"Waiting for {responder_name} to choose a creature with power 7 or more to defeat with Tiger Squirrel."
        if pending.action_key == "turf_the_surfer":
            return f"Waiting for {responder_name} to choose a creature that cannot block because of Turf the Surfer."
        if pending.action_key == "tusked_extorter":
            return f"Waiting for {responder_name} to choose a card to discard for Tusked Extorter."
        if pending.action_key == "wheatle":
            return (
                f"Waiting for {responder_name} to choose a number (1-10) for Wheatle."
            )
        return f"Waiting for {responder_name} to resolve a card action choice."

    def resolve_pending_card_action(self, selected_indices: list[int]) -> None:
        self._ensure_active()
        if self._pending_card_action_choice is None:
            raise ValueError("There is no pending card action choice.")

        pending = self._pending_card_action_choice
        self._pending_card_action_choice = None
        self._resolve_card_action_choice(pending, selected_indices)

    def _resolve_card_action_choice(
        self,
        pending: PendingCardActionChoice,
        selected_indices: list[int],
        apply_post_resolution_effects: bool = True,
    ) -> None:
        self._validate_pending_card_action_selection(pending, selected_indices)

        if pending.action_key == "brain_fly":
            self._apply_brain_fly_choice(pending, selected_indices)
        elif pending.action_key == "compost_dragon":
            self._apply_compost_dragon_choice(pending, selected_indices)
        elif pending.action_key == "count_draculeech":
            self._apply_count_draculeech_choice(pending, selected_indices)
        elif pending.action_key == "ferret_bomber":
            self._apply_ferret_bomber_choice(pending, selected_indices)
        elif pending.action_key == "explosive_toad":
            self._apply_explosive_toad_choice(pending, selected_indices)
        elif pending.action_key == "short_neck_giraffodile":
            self._apply_short_neck_giraffodile_choice(pending, selected_indices)
        elif pending.action_key == "snail_hydra":
            self._apply_snail_hydra_choice(pending, selected_indices)
        elif pending.action_key == "grave_robber":
            self._apply_grave_robber_choice(pending, selected_indices)
        elif pending.action_key == "harpy_mother":
            self._apply_harpy_mother_choice(pending, selected_indices)
        elif pending.action_key == "hyenix":
            self._apply_hyenix_choice(pending, selected_indices)
        elif pending.action_key == "hungry_hungry_hamster_give":
            self._apply_hungry_hungry_hamster_give_choice(pending, selected_indices)
        elif pending.action_key == "hungry_hungry_hamster_place":
            self._apply_hungry_hungry_hamster_place_choice(pending, selected_indices)
        elif pending.action_key == "shark_dog":
            self._apply_shark_dog_choice(pending, selected_indices)
        elif pending.action_key == "sluggernaut":
            self._apply_sluggernaut_choice(pending, selected_indices)
        elif pending.action_key == "tiger_squirrel":
            self._apply_tiger_squirrel_choice(pending, selected_indices)
        elif pending.action_key == "turf_the_surfer":
            self._apply_turf_the_surfer_choice(pending, selected_indices)
        elif pending.action_key == "tusked_extorter":
            self._apply_tusked_extorter_choice(pending, selected_indices)
        elif pending.action_key == "wheatle":
            self._apply_wheatle_choice(pending, selected_indices)
        else:
            raise ValueError("Unsupported pending card action choice.")

        if apply_post_resolution_effects:
            if self._pending_card_action_choice is not None:
                return
            self._process_next_hyenix_trigger_if_needed()
            if self._pending_card_action_choice is not None:
                return
            if pending.draw_up_to_hand_limit_after_resolution:
                self._draw_up_to_hand_limit_for_each_player_if_needed()
            self._recalculate_ongoing_effects()
            self._check_game_over()
            # Continue processing queued DEFEATED actions
            if (
                self._defeated_action_queue
                or self._pending_combat_finalization is not None
            ):
                self._process_next_defeated_action()
                return
            if self._pending_attack_continuation is not None:
                self._continue_attack_after_action_resolution()
                return
            if pending.auto_end_after_play:
                self._auto_end_turn_after_play_if_needed()
            if pending.auto_end_after_attack:
                self._auto_end_turn_after_attack_if_needed()
            if self._pending_defense_decision is not None:
                attacker = self._pending_defense_decision.attacker
                attacker_player = self.players[
                    self._pending_defense_decision.attacking_player_index
                ]
                if attacker not in attacker_player.cards_laid_out:
                    self.log.append(
                        f"{attacker_player.name}'s {attacker.name} is no longer on the battlefield. Attack is cancelled."
                    )
                    self._pending_defense_decision = None
                    self.game_state = GameState.ACTIVE
                    self._turn_action_taken = True
                    self._auto_end_turn_after_attack_if_needed()

    def _validate_pending_card_action_selection(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        if len(selected_indices) != len(set(selected_indices)):
            raise ValueError("Selected indices must be unique.")
        if not pending.min_choices <= len(selected_indices) <= pending.max_choices:
            if pending.min_choices == pending.max_choices:
                raise ValueError(
                    f"You must choose exactly {pending.min_choices} card(s)."
                )
            raise ValueError(
                f"You must choose between {pending.min_choices} and {pending.max_choices} cards."
            )
        invalid_indices = [
            index for index in selected_indices if index not in pending.eligible_indices
        ]
        if invalid_indices:
            raise ValueError("One or more selected cards are not eligible.")

    def _apply_brain_fly_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        opponent = self.players[pending.selection_owner_index]
        if not selected_indices:
            self.log.append(
                f"{owner.name}'s Brain Fly does not take control of a creature."
            )
            return
        # NOTE - PLAY effect should not be triggered as card was already PLAYED
        stolen_creature = opponent.cards_laid_out[selected_indices[0]]
        opponent.cards_laid_out.remove(stolen_creature)
        owner.cards_laid_out.append(stolen_creature)
        self.log.append(
            f"{owner.name}'s Brain Fly takes control of {stolen_creature.name}."
        )

    def _apply_compost_dragon_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        if not selected_indices:
            self.log.append(
                f"{owner.name}'s Compost Dragon has no card to play from the discard pile."
            )
            return
        card = owner.discard_pile.pop(selected_indices[0])
        self.log.append(f"{owner.name} plays {card.name} from their discard pile.")
        stolen = not pending.auto_end_after_play or self._play_is_stolen_by_mindbug
        self._finalize_played_card(
            owner_index=pending.responding_player_index,
            card=card,
            consume_turn_action=not stolen,
        )

    def _apply_count_draculeech_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        defeated_creature = enemy.cards_laid_out[selected_indices[0]]
        self._destroy_creature(enemy, defeated_creature)
        self.log.append(
            f"{owner.name}'s Count Draculeech defeats {defeated_creature.name}."
        )

    def _apply_ferret_bomber_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        responder = self.players[pending.responding_player_index]
        discarded_cards = [responder.hand[index] for index in sorted(selected_indices)]
        for card in discarded_cards:
            responder.hand.remove(card)
            responder.move_to_discard(card)
        # NOTE - Is this needed? Players should always draw anyway.
        responder.draw(len(discarded_cards))
        source_owner = self.players[1 - pending.responding_player_index]
        self.log.append(
            f"{source_owner.name}'s Ferret Bomber makes {responder.name} discard {len(discarded_cards)} cards."
        )

    def _apply_explosive_toad_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        if not selected_indices:
            self.log.append(f"{owner.name}'s Explosive Toad has no target to defeat.")
            return
        defeated_creature = enemy.cards_laid_out[selected_indices[0]]
        self._destroy_creature(enemy, defeated_creature)
        self.log.append(
            f"{owner.name}'s Explosive Toad defeats {defeated_creature.name}."
        )

    def _apply_short_neck_giraffodile_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        if not selected_indices:
            self.log.append(
                f"{owner.name}'s Short Neck Giraffodile has no card to play from the discard pile."
            )
            return
        drawn_cards = [
            owner.discard_pile.pop(index)
            for index in sorted(selected_indices, reverse=True)
        ]
        owner.hand.extend(drawn_cards)
        self.log.append(
            f"{owner.name} draws {len(drawn_cards)} cards from their discard pile."
        )

    def _apply_snail_hydra_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        enemy = self.players[pending.selection_owner_index]
        source_owner = self.players[1 - pending.selection_owner_index]
        defeated_creature = enemy.cards_laid_out[selected_indices[0]]
        self._destroy_creature(enemy, defeated_creature)
        self.log.append(
            f"{source_owner.name}'s Snail Hydra defeats {defeated_creature.name}."
        )

    def _apply_grave_robber_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        opponent = self.players[pending.selection_owner_index]
        card = opponent.discard_pile.pop(selected_indices[0])
        self.log.append(
            f"{owner.name} plays {card.name} from {opponent.name}'s discard pile."
        )
        # NOTE - same as in Compost Dragon case - if card is stolen by Mindbug, it should not consume turn action
        is_mindbug_stolen = (
            not pending.auto_end_after_play or self._play_is_stolen_by_mindbug
        )
        self._finalize_played_card(
            owner_index=pending.responding_player_index,
            card=card,
            consume_turn_action=not is_mindbug_stolen,
        )

    def _apply_harpy_mother_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        stolen_creatures = [enemy.cards_laid_out[i] for i in selected_indices]
        for creature in stolen_creatures:
            # NOTE - PLAY effect should not be triggered as card was already PLAYED
            enemy.cards_laid_out.remove(creature)
            owner.cards_laid_out.append(creature)
            self.log.append(
                f"{owner.name}'s Harpy Mother takes control of {creature.name}."
            )

    def _apply_hyenix_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        hyenix = pending.staged_card
        if hyenix is None:
            raise ValueError("Hyenix choice is missing the staged card.")
        if selected_indices[0] == 0:
            self.log.append(f"{owner.name} keeps Hyenix in their discard pile.")
            return
        if hyenix not in owner.discard_pile:
            self.log.append(
                f"{owner.name} cannot play Hyenix from their discard pile because it is no longer there."
            )
            return
        owner.discard_pile.remove(hyenix)
        self.log.append(
            f"{owner.name} plays Hyenix from their discard pile after losing life."
        )
        self._finalize_played_card(
            owner_index=pending.responding_player_index,
            card=hyenix,
            consume_turn_action=False,
        )

    def _apply_hungry_hungry_hamster_give_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        giving_player = self.players[pending.responding_player_index]
        receiving_player = self.players[1 - pending.responding_player_index]
        card = giving_player.hand.pop(selected_indices[0])
        # A card left the giver's hand, so refill hands before the follow-up choice.
        self._draw_up_to_hand_limit_for_each_player_if_needed()
        self.log.append(
            f"{giving_player.name} gives {card.name} to {receiving_player.name} because of Hungry Hungry Hamster."
        )
        self._set_pending_card_action_choice(
            action_key="hungry_hungry_hamster_place",
            source_card=pending.source_card,
            responding_player_index=1 - pending.responding_player_index,
            selection_owner_index=1 - pending.responding_player_index,
            selection_zone="options",
            eligible_indices=[0, 1],
            min_choices=1,
            max_choices=1,
            option_labels=["Put into hand", f"Play {card.name}"],
            staged_card=card,
            auto_end_after_play=pending.auto_end_after_play,
        )

    def _apply_hungry_hungry_hamster_place_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        giver = self.players[1 - pending.responding_player_index]
        card = pending.staged_card
        if card is None:
            raise ValueError("Hungry Hungry Hamster is missing the received card.")
        if selected_indices[0] == 0:
            owner.hand.append(card)
            self.log.append(
                f"{owner.name} puts {card.name} from {giver.name}'s hand into their hand because of Hungry Hungry Hamster."
            )
            return

        self.log.append(
            f"{owner.name} plays {card.name} from {giver.name}'s hand because of Hungry Hungry Hamster."
        )
        self._finalize_played_card(
            owner_index=pending.responding_player_index,
            card=card,
            consume_turn_action=False,
        )
        if self._pending_card_action_choice is not None:
            self._pending_card_action_choice.auto_end_after_play = (
                pending.auto_end_after_play
            )

    def _apply_shark_dog_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        defeated_creature = enemy.cards_laid_out[selected_indices[0]]
        self._destroy_creature(enemy, defeated_creature)
        self.log.append(
            f"{owner.name}'s Shark Dog defeats {defeated_creature.name} with power 6 or more."
        )

    def _apply_sluggernaut_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        card = pending.staged_card
        if card is None:
            raise ValueError("Sluggernaut choice is missing the staged card.")
        if selected_indices[0] == 0:
            card.chosen_form = "hunter"
            self.log.append(
                f"{owner.name}'s {card.name} becomes {CardSpecialType.HUNTER.value} with strength 5."
            )
        else:
            card.chosen_form = "frenzy"
            self.log.append(
                f"{owner.name}'s {card.name} becomes {CardSpecialType.FRENZY.value} with strength 8."
            )

    def _apply_tiger_squirrel_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        defeated_creature = enemy.cards_laid_out[selected_indices[0]]
        self._destroy_creature(enemy, defeated_creature)
        self.log.append(
            f"{owner.name}'s Tiger Squirrel defeats {defeated_creature.name} with power 7 or more."
        )

    def _apply_turf_the_surfer_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        enemy = self.players[pending.selection_owner_index]
        chosen_creature = enemy.cards_laid_out[selected_indices[0]]
        chosen_creature.temporary_cannot_block_until_turn_end = True
        chosen_creature.cannot_block = True
        self.log.append(
            f"{owner.name}'s Turf the Surfer makes {chosen_creature.name} unable to block this turn."
        )

    def _apply_tusked_extorter_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        responder = self.players[pending.responding_player_index]
        source_owner = self.players[1 - pending.responding_player_index]
        card = responder.hand[selected_indices[0]]
        responder.hand.remove(card)
        responder.move_to_discard(card)
        self.log.append(
            f"{source_owner.name}'s Tusked Extorter attacks {responder.name} and makes them discard {card.name}."
        )

    def _apply_wheatle_choice(
        self, pending: PendingCardActionChoice, selected_indices: list[int]
    ) -> None:
        owner = self.players[pending.responding_player_index]
        opponent = self.players[1 - pending.responding_player_index]
        chosen_number = selected_indices[0] + 1
        matching_cards = [
            card for card in opponent.hand if card.strength == chosen_number
        ]
        for card in matching_cards:
            opponent.hand.remove(card)
            owner.hand.append(card)
        if matching_cards:
            names = ", ".join(card.name for card in matching_cards)
            self.log.append(
                f"{owner.name}'s Wheatle takes {names} (strength {chosen_number}) from {opponent.name}'s hand."
            )
        else:
            self.log.append(
                f"{owner.name}'s Wheatle finds no cards with strength {chosen_number} in {opponent.name}'s hand."
            )

    def lose_life(
        self,
        player_index: int,
        amount: int = 1,
        *,
        auto_end_after_play: bool = False,
        auto_end_after_attack: bool = False,
    ) -> int:
        player = self.players[player_index]
        lost_life = player.lose_life(amount)
        if lost_life > 0:
            self._queue_hyenix_triggers_for_player(
                player_index,
                auto_end_after_play=auto_end_after_play,
                auto_end_after_attack=auto_end_after_attack,
            )
        return lost_life

    def _queue_hyenix_triggers_for_player(
        self,
        player_index: int,
        *,
        auto_end_after_play: bool = False,
        auto_end_after_attack: bool = False,
    ) -> None:
        queued_by_card_id = {
            id(trigger.card): trigger
            for trigger in self._pending_hyenix_triggers
            if trigger.owner_index == player_index
        }
        for card in self.players[player_index].discard_pile:
            if card.name != "Hyenix":
                continue
            queued = queued_by_card_id.get(id(card))
            if queued is None:
                self._pending_hyenix_triggers.append(
                    PendingHyenixTrigger(
                        owner_index=player_index,
                        card=card,
                        auto_end_after_play=auto_end_after_play,
                        auto_end_after_attack=auto_end_after_attack,
                    )
                )
                continue
            queued.auto_end_after_play = (
                queued.auto_end_after_play or auto_end_after_play
            )
            queued.auto_end_after_attack = (
                queued.auto_end_after_attack or auto_end_after_attack
            )

    def _process_next_hyenix_trigger_if_needed(self) -> None:
        if self.game_state == GameState.GAME_OVER:
            self._pending_hyenix_triggers = []
            return
        if self._pending_card_action_choice is not None:
            return
        while self._pending_hyenix_triggers:
            trigger = self._pending_hyenix_triggers.pop(0)
            owner = self.players[trigger.owner_index]
            if trigger.card not in owner.discard_pile:
                continue
            self._set_pending_card_action_choice(
                action_key="hyenix",
                source_card=trigger.card,
                responding_player_index=trigger.owner_index,
                selection_owner_index=trigger.owner_index,
                selection_zone="options",
                eligible_indices=[0, 1],
                min_choices=1,
                max_choices=1,
                option_labels=["Keep Hyenix in discard pile", "Play Hyenix"],
                staged_card=trigger.card,
                auto_end_after_play=trigger.auto_end_after_play,
                auto_end_after_attack=trigger.auto_end_after_attack,
            )
            return

    def queue_sluggernaut_form_choice(self, card: Card, owner: Player) -> None:
        owner_index = self.players.index(owner)
        for pending in self._pending_sluggernaut_form_choices:
            if pending.card is card:
                return
        self._pending_sluggernaut_form_choices.append(
            PendingSluggernautFormChoice(owner_index=owner_index, card=card)
        )

    def _process_next_sluggernaut_form_choice_if_needed(self) -> None:
        if self.game_state == GameState.GAME_OVER:
            self._pending_sluggernaut_form_choices = []
            return
        if self._pending_card_action_choice is not None:
            return
        while self._pending_sluggernaut_form_choices:
            pending = self._pending_sluggernaut_form_choices.pop(0)
            owner = self.players[pending.owner_index]
            card = pending.card
            # Skip stale entries: card must still be in play, exhausted, and unset.
            if card not in owner.cards_laid_out:
                continue
            if card.tough_charges != 0:
                continue
            if getattr(card, "chosen_form", None) is not None:
                continue
            self._set_pending_card_action_choice(
                action_key="sluggernaut",
                source_card=card,
                responding_player_index=pending.owner_index,
                selection_owner_index=pending.owner_index,
                selection_zone="options",
                eligible_indices=[0, 1],
                min_choices=1,
                max_choices=1,
                option_labels=[
                    f"{CardSpecialType.HUNTER.value} (strength 5)",
                    f"{CardSpecialType.FRENZY.value} (strength 8)",
                ],
                staged_card=card,
            )
            return

    # TODO - do not put defender_index as argument to attack function, instead create defend function that takes attacker and defender and is used inside attack function
    def attack(
        self,
        attacker_index: int,
        defender_index: Optional[int] = None,
    ) -> None:
        self._ensure_active()
        self._ensure_no_pending_resolution()
        self._recalculate_ongoing_effects()
        attacker_owner = self.current_player
        defender_owner = self.opponent
        is_resolving_frenzy_attack = self._pending_frenzy_attacker_id is not None

        if (
            self.enforce_turn_action_limit
            and self._turn_action_taken
            and not is_resolving_frenzy_attack
        ):
            raise ValueError("You already took your action this turn.")

        if attacker_index < 0 or attacker_index >= len(attacker_owner.cards_laid_out):
            raise ValueError("Invalid attacker index.")

        if len(attacker_owner.cards_laid_out) == 0:
            raise ValueError("No cards laid out to attack.")

        attacker = attacker_owner.cards_laid_out[attacker_index]
        if (
            is_resolving_frenzy_attack
            and id(attacker) != self._pending_frenzy_attacker_id
        ):
            raise ValueError(
                "You must use the same FRENZY creature for the bonus attack."
            )
        if attacker.cannot_attack:
            raise ValueError(f"{attacker.name} cannot attack right now.")
        attacks_used = self._attacks_this_turn.get(id(attacker), 0)
        max_attacks = 2 if CardSpecialType.FRENZY in attacker.special_types else 1
        if attacks_used >= max_attacks:
            raise ValueError(
                f"{attacker.name} cannot attack more than {max_attacks} times this turn."
            )
        self._attacks_this_turn[id(attacker)] = attacks_used + 1

        # Resolve HUNTER target before ATTACK action trigger
        attacker_has_hunter = CardSpecialType.HUNTER in attacker.special_types
        hunter_defender: Optional[Card] = None
        if defender_index is not None and not attacker_has_hunter:
            raise ValueError(
                "Cannot target attack with a non-HUNTER attacker. Remove target and attack again."
            )
        if attacker_has_hunter and defender_index is not None:
            if defender_index < 0 or defender_index >= len(
                defender_owner.cards_laid_out
            ):
                raise ValueError("Invalid defender index.")
            hunter_defender = defender_owner.cards_laid_out[defender_index]

        # Trigger action if attacker has an action type
        if attacker.action_type == CardActionType.ATTACK:
            attacker.trigger_action(self)
            # ATTACK actions that cause the opponent to lose life (e.g. Turbo Bug,
            # Chameleon Sniper) only queue Hyenix triggers; surface them now so
            # the opponent gets the choice to play Hyenix from their discard pile
            # before combat continues.
            if self._pending_card_action_choice is None:
                self._process_next_hyenix_trigger_if_needed()
            if self._pending_card_action_choice is not None:
                # Action needs player input — pause attack and continue after choice resolves
                self._pending_attack_continuation = PendingAttackContinuation(
                    attacker=attacker,
                    attacker_owner_index=self.turn,
                    defender=hunter_defender,
                    defender_owner_index=1 - self.turn,
                )
                return
            self._draw_up_to_hand_limit_for_each_player_if_needed()
            self._check_game_over()
            # NOTE - prevents the code from continuing to set up defense decisions or direct attacks, that would overwrite GAME_OVER with AWAITING_DEFENSE
            if self.game_state == GameState.GAME_OVER:
                return
            # ATTACK action can remove attacker before combat resolution (e.g. Snail Hydra attacks and destroys Explosive Toad, which then destroys Snail Hydra).
            if attacker not in attacker_owner.cards_laid_out:
                self._turn_action_taken = True
                self._pending_frenzy_attacker_id = None
                self.log.append(
                    f"{attacker_owner.name}'s {attacker.name} is no longer on the battlefield. Attack is cancelled."
                )
                self._auto_end_turn_after_attack_if_needed()
                return
            # ATTACK action may have defeated the HUNTER target before combat
            if (
                hunter_defender is not None
                and hunter_defender not in defender_owner.cards_laid_out
            ):
                self.log.append(
                    f"{defender_owner.name}'s {hunter_defender.name} was defeated. Combat is cancelled."
                )
                self._finalize_attack_action(attacker_owner, attacker)
                return

        if hunter_defender is not None:
            self._resolve_combat(
                attacker_owner, defender_owner, attacker, hunter_defender
            )
            return

        eligible_defender_indices = self.get_eligible_defender_indices(
            attacker_index=attacker_index,
            hunter_target_override=False,
        )
        if len(eligible_defender_indices) == 0:
            self._resolve_direct_attack(attacker_owner, defender_owner, attacker)
            return

        self._pending_defense_decision = PendingDefenseDecision(
            attacking_player_index=self.turn,
            defending_player_index=1 - self.turn,
            attacker=attacker,
        )
        self.game_state = GameState.AWAITING_DEFENSE
        self.log.append(
            f"Waiting for {defender_owner.name} to choose a blocker or lose 1 life."
        )

    def _continue_attack_after_action_resolution(self) -> None:
        cont = self._pending_attack_continuation
        assert cont is not None
        self._pending_attack_continuation = None

        self._draw_up_to_hand_limit_for_each_player_if_needed()

        if self.game_state == GameState.GAME_OVER:
            return

        attacker_owner = self.players[cont.attacker_owner_index]
        defender_owner = self.players[cont.defender_owner_index]
        attacker = cont.attacker

        if attacker not in attacker_owner.cards_laid_out:
            self._turn_action_taken = True
            self._pending_frenzy_attacker_id = None
            self.log.append(
                f"{attacker_owner.name}'s {attacker.name} is no longer on the battlefield. Attack is cancelled."
            )
            self._auto_end_turn_after_attack_if_needed()
            return

        # HUNTER target was defeated by the ATTACK action
        if (
            cont.defender is not None
            and cont.defender not in defender_owner.cards_laid_out
        ):
            self.log.append(
                f"{defender_owner.name}'s {cont.defender.name} was defeated. Combat is cancelled."
            )
            self._finalize_attack_action(attacker_owner, attacker)
            return

        # HUNTER target survived — proceed with combat
        if cont.defender is not None:
            self._resolve_combat(
                attacker_owner, defender_owner, attacker, cont.defender
            )
            return

        # Non-HUNTER attacker — proceed with defense decision
        attacker_index = attacker_owner.cards_laid_out.index(attacker)
        eligible_defender_indices = self.get_eligible_defender_indices(
            attacker_index=attacker_index,
            hunter_target_override=False,
        )
        if len(eligible_defender_indices) == 0:
            self._resolve_direct_attack(attacker_owner, defender_owner, attacker)
            return

        self._pending_defense_decision = PendingDefenseDecision(
            attacking_player_index=cont.attacker_owner_index,
            defending_player_index=cont.defender_owner_index,
            attacker=attacker,
        )
        self.game_state = GameState.AWAITING_DEFENSE
        self.log.append(
            f"Waiting for {defender_owner.name} to choose a blocker or lose 1 life."
        )

    def resolve_pending_defeated_ordering(self, ordered_indices: list[int]) -> None:
        self._ensure_active()
        if self._pending_defeated_ordering is None:
            raise ValueError("There is no pending DEFEATED ordering choice.")

        pending = self._pending_defeated_ordering
        if len(ordered_indices) != len(pending.entries):
            raise ValueError(f"Must order all {len(pending.entries)} DEFEATED actions.")
        if sorted(ordered_indices) != list(range(len(pending.entries))):
            raise ValueError("Invalid ordering indices.")

        self._defeated_action_queue = [pending.entries[i] for i in ordered_indices]
        self._pending_defeated_ordering = None

        self._process_next_defeated_action()

    def _process_next_defeated_action(self) -> None:
        if not self._defeated_action_queue:
            self._draw_up_to_hand_limit_for_each_player_if_needed()
            self._recalculate_ongoing_effects()
            self._check_game_over()

            if self._pending_combat_finalization is not None:
                fin = self._pending_combat_finalization
                self._pending_combat_finalization = None
                attacker_owner = self.players[fin.attacker_owner_index]
                self._finalize_attack_action(attacker_owner, fin.attacker)
            return

        if self.game_state == GameState.GAME_OVER:
            self._defeated_action_queue = []
            self._pending_combat_finalization = None
            return

        entry = self._defeated_action_queue.pop(0)

        self.log.append(
            f"{entry.owner_name}'s {entry.creature.name} triggers its DEFEATED action."
        )
        entry.creature.trigger_action(self)

        if self._pending_card_action_choice is not None:
            # Wait for card action to resolve; post-resolution will continue the queue
            return

        self._draw_up_to_hand_limit_for_each_player_if_needed()
        self._recalculate_ongoing_effects()
        self._check_game_over()
        self._process_next_defeated_action()

    def resolve_brain_fly_action(self, source_card: Card) -> None:
        eligible_indices = [
            index
            for index, card in enumerate(self.opponent.cards_laid_out)
            if card.strength >= 6
        ]
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Brain Fly does not take control of a creature."
            )
            return
        self._set_pending_card_action_choice(
            action_key="brain_fly",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_play=True,
        )

    def resolve_compost_dragon_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.current_player.discard_pile)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Compost Dragon has no card to play from the discard pile."
            )
            return
        self._set_pending_card_action_choice(
            action_key="compost_dragon",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=self.turn,
            selection_zone="discard",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_play=True,
        )

    def resolve_count_draculeech_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.cards_laid_out)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Count Draculeech does not defeat a creature because {self.opponent.name} has no creatures on the battlefield."
            )
            return
        self._set_pending_card_action_choice(
            action_key="count_draculeech",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_attack=True,
        )

    def resolve_ferret_bomber_action(self, source_card: Card) -> None:
        discard_count = min(2, len(self.opponent.hand))
        if discard_count == 0:
            self.log.append(
                f"{self.opponent.name}'s Ferret Bomber does not make {self.current_player.name} discard because they have no cards in their hand."
            )
            return
        self._set_pending_card_action_choice(
            action_key="ferret_bomber",
            source_card=source_card,
            responding_player_index=1 - self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="hand",
            eligible_indices=list(range(len(self.opponent.hand))),
            min_choices=discard_count,
            max_choices=discard_count,
            auto_end_after_play=True,
        )

    def resolve_explosive_toad_action(self, source_card: Card) -> None:
        owner = next(
            (
                player_index
                for player_index, player in enumerate(self.players)
                if source_card in player.cards_laid_out
                or source_card in player.discard_pile
            ),
            None,
        )
        if owner is None:
            self.log.append(f"{source_card.name} cannot resolve DEFEATED action.")
            return

        enemy = 1 - owner
        if len(self.players[enemy].cards_laid_out) == 0:
            self.log.append(
                f"{self.players[owner].name}'s Explosive Toad has no target to defeat."
            )
            return
        self._set_pending_card_action_choice(
            action_key="explosive_toad",
            source_card=source_card,
            responding_player_index=owner,
            selection_owner_index=enemy,
            selection_zone="battlefield",
            eligible_indices=list(range(len(self.players[enemy].cards_laid_out))),
            min_choices=1,
            max_choices=1,
            draw_up_to_hand_limit_after_resolution=True,
            auto_end_after_attack=True,
        )

    def resolve_short_neck_giraffodile_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.current_player.discard_pile)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Short Neck Giraffodile has no card to play from the discard pile."
            )
            return
        self._set_pending_card_action_choice(
            action_key="short_neck_giraffodile",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=self.turn,
            selection_zone="discard",
            eligible_indices=eligible_indices,
            min_choices=min(2, len(eligible_indices)),
            max_choices=min(2, len(eligible_indices)),
            auto_end_after_play=True,
        )

    def resolve_snail_hydra_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.cards_laid_out)))
        if not eligible_indices:
            self.log.append(
                f"{self.opponent.name}'s Snail Hydra has no creature to defeat."
            )
            return
        self._set_pending_card_action_choice(
            action_key="snail_hydra",
            source_card=source_card,
            responding_player_index=self.turn,  # NOTE - current player chooses the creature to defeat
            selection_owner_index=1
            - self.turn,  # NOTE - target selection points to opponent battlefield
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_attack=True,
        )

    def resolve_grave_robber_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.discard_pile)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Grave Robber does not play a card from {self.opponent.name}'s discard pile because they have no cards in their discard pile."
            )
            return
        self._set_pending_card_action_choice(
            action_key="grave_robber",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="discard",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_play=True,
        )

    def resolve_harpy_mother_action(self, source_card: Card) -> None:
        owner = next(
            (
                player_index
                for player_index, player in enumerate(self.players)
                if source_card in player.cards_laid_out
                or source_card in player.discard_pile
            ),
            None,
        )
        if owner is None:
            self.log.append(f"{source_card.name} cannot resolve DEFEATED action.")
            return
        enemy = 1 - owner
        eligible_indices = [
            i
            for i, card in enumerate(self.players[enemy].cards_laid_out)
            if card.strength <= 5
        ]
        if not eligible_indices:
            self.log.append(
                f"{self.players[owner].name}'s Harpy Mother does not take control of any enemy creatures with power 5 or less."
            )
            return
        max_choices = min(2, len(eligible_indices))
        self._set_pending_card_action_choice(
            action_key="harpy_mother",
            source_card=source_card,
            responding_player_index=owner,
            selection_owner_index=enemy,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=max_choices,
            draw_up_to_hand_limit_after_resolution=True,  # Probbaly redundant in Harpy mother case
            auto_end_after_attack=True,  # NOTE - this is here so that when attack harpy mother, turn auto-ends after combat
        )

    def resolve_hungry_hungry_hamster_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.hand)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Hungry Hungry Hamster does not receive a card from {self.opponent.name}'s hand because they have no cards in their hand."
            )
            return
        self._set_pending_card_action_choice(
            action_key="hungry_hungry_hamster_give",
            source_card=source_card,
            responding_player_index=1 - self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="hand",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_play=True,
        )

    def resolve_shark_dog_action(self, source_card: Card) -> None:
        eligible_indices = [
            i
            for i, card in enumerate(self.opponent.cards_laid_out)
            if card.strength >= 6
        ]
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Shark Dog does not defeat a creature."
            )
            return
        self._set_pending_card_action_choice(
            action_key="shark_dog",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_attack=True,
        )

    def resolve_tiger_squirrel_action(self, source_card: Card) -> None:
        eligible_indices = [
            i
            for i, card in enumerate(self.opponent.cards_laid_out)
            if card.strength >= 7
        ]
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Tiger Squirrel does not defeat a creature."
            )
            return
        self._set_pending_card_action_choice(
            action_key="tiger_squirrel",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_play=True,
        )

    def resolve_turf_the_surfer_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.cards_laid_out)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Turf the Surfer does not choose a creature because {self.opponent.name} has no creatures on the battlefield."
            )
            return
        self._set_pending_card_action_choice(
            action_key="turf_the_surfer",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="battlefield",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_attack=True,
        )

    def resolve_tusked_extorter_action(self, source_card: Card) -> None:
        eligible_indices = list(range(len(self.opponent.hand)))
        if not eligible_indices:
            self.log.append(
                f"{self.current_player.name}'s Tusked Extorter does not make {self.opponent.name} discard because they have no cards in their hand."
            )
            return
        self._set_pending_card_action_choice(
            action_key="tusked_extorter",
            source_card=source_card,
            responding_player_index=1 - self.turn,
            selection_owner_index=1 - self.turn,
            selection_zone="hand",
            eligible_indices=eligible_indices,
            min_choices=1,
            max_choices=1,
            auto_end_after_attack=True,
        )

    def resolve_wheatle_action(self, source_card: Card) -> None:
        self._set_pending_card_action_choice(
            action_key="wheatle",
            source_card=source_card,
            responding_player_index=self.turn,
            selection_owner_index=self.turn,
            selection_zone="options",
            eligible_indices=list(range(10)),
            min_choices=1,
            max_choices=1,
            option_labels=[str(i) for i in range(1, 11)],
            auto_end_after_attack=True,
        )

    def defend(self, defender_index: Optional[int] = None) -> None:
        self._ensure_active()
        if self._pending_defense_decision is None:
            raise ValueError("There is no pending defense decision.")

        pending = self._pending_defense_decision
        attacker_owner = self.players[pending.attacking_player_index]
        defender_owner = self.players[pending.defending_player_index]
        attacker = pending.attacker

        self._pending_defense_decision = None
        self.game_state = GameState.ACTIVE

        if attacker not in attacker_owner.cards_laid_out:
            raise ValueError("The attacking creature is no longer on the battlefield.")

        if defender_index is None:
            self._resolve_direct_attack(attacker_owner, defender_owner, attacker)
            return

        if defender_index < 0 or defender_index >= len(defender_owner.cards_laid_out):
            raise ValueError("Invalid defender index.")

        defender = defender_owner.cards_laid_out[defender_index]
        self._ensure_legal_blocker(attacker, defender)
        self._resolve_combat(attacker_owner, defender_owner, attacker, defender)

    def _is_eligible_defender(
        self,
        attacker: Card,
        defender: Card,
        hunter_target_override: bool = True,
    ) -> bool:
        if hunter_target_override and CardSpecialType.HUNTER in attacker.special_types:
            return True
        try:
            self._ensure_legal_blocker(attacker, defender)
            return True
        except ValueError:
            return False

    def get_eligible_defender_indices(
        self,
        attacker_index: int,
        hunter_target_override: bool = True,
    ) -> list[int]:
        self._ensure_active()
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
        for player in self.players:
            for card in player.cards_laid_out:
                card.temporary_cannot_block_until_turn_end = False
        self.turn = 1 - self.turn
        self._attacks_this_turn = {}
        self._turn_action_taken = False
        self._pending_frenzy_attacker_id = None
        self._pending_defense_decision = None
        self._recalculate_ongoing_effects()
        self.game_state = GameState.START_TURN
        self.log.append(f"Turn passes to {self.current_player.name}.")

    def can_end_turn_manually(self) -> bool:
        return (
            self.game_state != GameState.GAME_OVER
            and self._pending_mindbug_decision is None
            and self._pending_defense_decision is None
            and self._pending_card_action_choice is None
            and self._pending_frenzy_attacker_id is not None
        )

    def get_state(self, viewer_index: Optional[int] = None) -> dict[str, Any]:
        if viewer_index is not None:
            return self._build_player_view(viewer_index)

        turn_player = self.current_player
        players_state = [
            self._serialize_player(index) for index in range(len(self.players))
        ]
        indexed_turn_hand = ", ".join(
            f"{index}: {card.short_label()}"
            for index, card in enumerate(turn_player.hand)
        )
        for player_state in players_state:
            if player_state["name"] == turn_player.name:
                # Backward compatibility: older UIs only render `hand_count`.
                player_state["hand_count"] = (
                    f"{len(turn_player.hand)} ({indexed_turn_hand if indexed_turn_hand else '-'})"
                )
                break
        return {
            "game_state": self.game_state.value,
            "turn_player": turn_player.name,
            "winner": None if not self.winner else self.winner.name,
            "turn_hand": [card.short_label() for card in turn_player.hand],
            "players": players_state,
            "log": list(self.log[-10:]),
            "pending_defense": self._serialize_pending_defense(),
            "pending_card_action": self._serialize_pending_card_action(),
        }

    def _serialize_player(
        self, player_index: int, include_hand: bool = True
    ) -> dict[str, Any]:
        player = self.players[player_index]
        return {
            "player_index": player_index,
            "name": player.name,
            "lives": player.number_of_lives,
            "mindbugs_remaining": player.mindbugs_remaining,
            "hand_count": len(player.hand),
            "hand": (
                [card.short_label() for card in player.hand] if include_hand else []
            ),
            "battlefield": [c.short_label() for c in player.cards_laid_out],
            "discard_count": len(player.discard_pile),
            "discard": [card.short_label() for card in player.discard_pile],
            "draw_count": len(player.draw_pile.cards),
        }

    def _destroy_creature(
        self,
        owner: Player,
        creature: Card,
        ignore_tough: bool = False,
        defer_defeated_action: bool = False,
    ) -> bool:
        # TODO -  refactor - returned boolean is used
        if (
            CardSpecialType.TOUGH in creature.special_types
            and creature.tough_charges > 0
            and not ignore_tough
        ):
            creature.tough_charges -= 1
            self.log.append(f"{creature.name} survives due to TOUGH.")
            # This is here to cover future cards effects
            self._draw_up_to_hand_limit_for_each_player_if_needed()
            self._recalculate_ongoing_effects()  # this is here to cover that The_pack gets SNEAKY when exhaused
            self._check_game_over()
            return False
        owner.cards_laid_out.remove(creature)
        owner.move_to_discard(creature)
        self.log.append(f"{owner.name}'s {creature.name} is defeated.")

        if (
            creature.action_type == CardActionType.DEFEATED
            and not defer_defeated_action
        ):
            creature.trigger_action(self)
            if self._pending_card_action_choice is None:
                self._draw_up_to_hand_limit_for_each_player_if_needed()
            self.log.append(
                f"{owner.name}'s {creature.name} is defeated and triggers its DEFEATED action."
            )

        self._recalculate_ongoing_effects()
        self._check_game_over()
        return creature.action_type == CardActionType.DEFEATED and defer_defeated_action

    def _is_defeated(self, defender: Card, attacker: Card) -> bool:
        if CardSpecialType.POISONOUS in attacker.special_types:
            return True
        return attacker.strength >= defender.strength

    def _check_game_over(self) -> None:
        for player in self.players:
            if player.number_of_lives <= 0 or (
                len(player.cards_laid_out) == 0
                and len(player.hand) == 0
                and len(player.draw_pile.cards) == 0
            ):
                self.game_state = GameState.GAME_OVER
                self.winner = (
                    self.players[0] if self.players[1] == player else self.players[1]
                )
                self.log.append(f"{self.winner.name} wins.")

    def surrender(self, player_index: int) -> None:
        self._ensure_active()
        surrendering = self.players[player_index]
        self.winner = (
            self.players[0] if self.players[1] == surrendering else self.players[1]
        )
        self.game_state = GameState.GAME_OVER
        self.log.append(f"{surrendering.name} surrendered. {self.winner.name} wins.")

    def _ensure_active(self) -> None:
        if self.game_state == GameState.GAME_OVER:
            raise ValueError("Game is already over.")

    def _ensure_no_pending_resolution(self) -> None:
        if self._pending_mindbug_decision is not None:
            responder = self.players[
                self._pending_mindbug_decision.responding_player_index
            ]
            raise ValueError(
                f"Waiting for {responder.name} to decide whether to use Mindbug."
            )
        if self._pending_defense_decision is not None:
            defender = self.players[
                self._pending_defense_decision.defending_player_index
            ]
            raise ValueError(
                f"Waiting for {defender.name} to choose a blocker or lose 1 life."
            )
        if self._pending_card_action_choice is not None:
            responder = self.players[
                self._pending_card_action_choice.responding_player_index
            ]
            raise ValueError(
                f"Waiting for {responder.name} to resolve a card action choice."
            )
        if self._pending_defeated_ordering is not None:
            responder = self.players[
                self._pending_defeated_ordering.responding_player_index
            ]
            raise ValueError(
                f"Waiting for {responder.name} to choose the order of DEFEATED actions."
            )

    # TODO - refactor - do not allow to select not eligible blockers
    def _ensure_legal_blocker(self, attacker: Card, defender: Card) -> None:
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
            raise ValueError(f"{defender.name} is too weak to block {attacker.name}.")
        if (
            attacker.requires_blocker_with_no_special_types
            and len(defender.special_types) > 0
        ):
            raise ValueError(
                f"{defender.name} cannot block {attacker.name} because only creatures with no keywords can block it."
            )

    def _finalize_played_card(
        self,
        owner_index: int,
        card: Card,
        consume_turn_action: bool = True,
    ) -> None:
        owner = self.players[owner_index]
        owner.cards_laid_out.append(card)
        self._recalculate_ongoing_effects()
        if (
            card.action_type == CardActionType.PLAY
            and not owner.cannot_activate_play_effects
        ):
            original_turn = self.turn
            self.turn = owner_index
            stolen = not consume_turn_action
            self._play_is_stolen_by_mindbug = stolen
            try:
                card.trigger_action(self)
            finally:
                self.turn = original_turn
                self._play_is_stolen_by_mindbug = False
            # When stolen by Mindbug (consume_turn_action=False), the original player
            # retains their turn after the pending choice resolves — do not auto-end it.
            if stolen and self._pending_card_action_choice is not None:
                self._pending_card_action_choice.auto_end_after_play = False
            self._recalculate_ongoing_effects()

        self._check_game_over()
        self._process_next_hyenix_trigger_if_needed()
        if self.enforce_turn_action_limit and consume_turn_action:
            self._turn_action_taken = True
            self._pending_frenzy_attacker_id = None

    def _resolve_direct_attack(
        self, attacker_owner: Player, defender_owner: Player, attacker: Card
    ) -> None:
        lost_life = self.lose_life(
            self.players.index(defender_owner), 1, auto_end_after_attack=True
        )
        if lost_life > 0:
            self.log.append(
                f"{attacker_owner.name}'s {attacker.name} attacks directly for {lost_life} life."
            )
        else:
            self.log.append(
                f"{attacker_owner.name}'s {attacker.name} attacks directly, but {defender_owner.name} cannot lose life."
            )
        self._check_game_over()
        self._process_next_hyenix_trigger_if_needed()
        self._finalize_attack_action(attacker_owner, attacker)

    def _resolve_combat(
        self,
        attacker_owner: Player,
        defender_owner: Player,
        attacker: Card,
        defender: Card,
    ) -> None:
        self.log.append(
            f"{attacker_owner.name}'s {attacker.name} attacks {defender_owner.name}'s {defender.name}."
        )

        attacker_defeated = self._is_defeated(attacker, defender)
        defender_defeated = self._is_defeated(defender, attacker)

        # Check if both will die and both have DEFEATED actions (need ordering)
        need_ordering = (
            attacker_defeated
            and defender_defeated
            and attacker.action_type == CardActionType.DEFEATED
            and defender.action_type == CardActionType.DEFEATED
        )

        deferred_entries: list[DefeatedCreatureEntry] = []

        if attacker_defeated:
            was_deferred = self._destroy_creature(
                attacker_owner, attacker, defer_defeated_action=need_ordering
            )
            if was_deferred:
                deferred_entries.append(
                    DefeatedCreatureEntry(
                        owner_index=self.players.index(attacker_owner),
                        creature=attacker,
                        owner_name=attacker_owner.name,
                        card_label=attacker.short_label(),
                    )
                )
        # Note - we must check that defender is still in cards_laid out because it can be destroyed by an attacker's DEFEATED action
        if defender_defeated and defender in defender_owner.cards_laid_out:
            was_deferred = self._destroy_creature(
                defender_owner, defender, defer_defeated_action=need_ordering
            )
            if was_deferred:
                deferred_entries.append(
                    DefeatedCreatureEntry(
                        owner_index=self.players.index(defender_owner),
                        creature=defender,
                        owner_name=defender_owner.name,
                        card_label=defender.short_label(),
                    )
                )

        if len(deferred_entries) >= 2:
            self._pending_combat_finalization = PendingCombatFinalization(
                attacker=attacker,
                attacker_owner_index=self.players.index(attacker_owner),
            )
            self._pending_defeated_ordering = PendingDefeatedOrdering(
                responding_player_index=self.turn,
                entries=deferred_entries,
            )
            self.log.append(
                f"Multiple DEFEATED actions triggered. {self.current_player.name} must choose the trigger order."
            )
            return

        # If ordering was attempted but <2 actually deferred (TOUGH saved one),
        # trigger any single deferred action now
        if need_ordering and len(deferred_entries) == 1:
            entry = deferred_entries[0]
            entry.creature.trigger_action(self)
            if self._pending_card_action_choice is None:
                self._draw_up_to_hand_limit_for_each_player_if_needed()
            self.log.append(
                f"{entry.owner_name}'s {entry.creature.name} triggers its DEFEATED action."
            )
            self._recalculate_ongoing_effects()
            self._check_game_over()

        self._finalize_attack_action(attacker_owner, attacker)

    def _finalize_attack_action(self, attacker_owner: Player, attacker: Card) -> None:
        if not self.enforce_turn_action_limit:
            self._pending_frenzy_attacker_id = None
            self._auto_end_turn_after_attack_if_needed()
            return

        self._turn_action_taken = True
        if (
            CardSpecialType.FRENZY in attacker.special_types
            and attacker in attacker_owner.cards_laid_out
            and self._attacks_this_turn.get(id(attacker), 0) == 1
            and self.game_state != GameState.GAME_OVER
        ):
            self._pending_frenzy_attacker_id = id(attacker)
            self.log.append(
                f"{attacker.name} may attack one more time this turn due to FRENZY."
            )
            return

        self._pending_frenzy_attacker_id = None
        self._auto_end_turn_after_attack_if_needed()

    def _build_player_view(self, viewer_index: int) -> dict[str, Any]:
        viewer = self.players[viewer_index]
        opponent_index = 1 - viewer_index
        opponent = self.players[opponent_index]
        pending_mindbug = None
        if self._pending_mindbug_decision is not None:
            pending_mindbug = {
                "acting_player_name": self.players[
                    self._pending_mindbug_decision.acting_player_index
                ].name,
                "responding_player_name": self.players[
                    self._pending_mindbug_decision.responding_player_index
                ].name,
                "card_label": self._pending_mindbug_decision.card.short_label(),
                "response_required_from_viewer": self._pending_mindbug_decision.responding_player_index
                == viewer_index,
            }
        pending_defense = None
        if self._pending_defense_decision is not None:
            pending_defense = {
                "attacking_player_name": self.players[
                    self._pending_defense_decision.attacking_player_index
                ].name,
                "defending_player_name": self.players[
                    self._pending_defense_decision.defending_player_index
                ].name,
                "attacker_label": self._pending_defense_decision.attacker.short_label(),
                "response_required_from_viewer": self._pending_defense_decision.defending_player_index
                == viewer_index,
                "eligible_defender_indices": self._get_pending_defense_eligible_indices(),
            }
        pending_card_action = self._serialize_pending_card_action_for_viewer(
            viewer_index
        )
        pending_defeated_ordering = None
        if self._pending_defeated_ordering is not None:
            pending_defeated_ordering = {
                "responding_player_name": self.players[
                    self._pending_defeated_ordering.responding_player_index
                ].name,
                "response_required_from_viewer": (
                    self._pending_defeated_ordering.responding_player_index
                    == viewer_index
                ),
                "entries": [
                    {
                        "owner_name": entry.owner_name,
                        "card_label": entry.card_label,
                    }
                    for entry in self._pending_defeated_ordering.entries
                ],
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
            "pending_defense": pending_defense,
            "pending_card_action": pending_card_action,
            "pending_frenzy_attacker_index": self._get_pending_frenzy_attacker_index(
                viewer_index
            ),
            "pending_defeated_ordering": pending_defeated_ordering,
        }

    def _serialize_pending_defense(self) -> dict[str, Any] | None:
        if self._pending_defense_decision is None:
            return None
        return {
            "attacking_player_name": self.players[
                self._pending_defense_decision.attacking_player_index
            ].name,
            "defending_player_name": self.players[
                self._pending_defense_decision.defending_player_index
            ].name,
            "attacker_label": self._pending_defense_decision.attacker.short_label(),
            "eligible_defender_indices": self._get_pending_defense_eligible_indices(),
        }

    def _serialize_pending_card_action(self) -> dict[str, Any] | None:
        if self._pending_card_action_choice is None:
            return None
        pending = self._pending_card_action_choice
        return {
            "action_key": pending.action_key,
            "source_card_label": pending.source_card.short_label(),
            "responding_player_name": self.players[
                pending.responding_player_index
            ].name,
            "selection_owner_name": self.players[pending.selection_owner_index].name,
            "selection_zone": pending.selection_zone,
            "eligible_indices": list(pending.eligible_indices),
            "min_choices": pending.min_choices,
            "max_choices": pending.max_choices,
            "option_labels": (
                list(pending.option_labels) if pending.option_labels else None
            ),
            "staged_card_label": (
                pending.staged_card.short_label()
                if pending.staged_card is not None
                else None
            ),
        }

    def _serialize_pending_card_action_for_viewer(
        self, viewer_index: int
    ) -> dict[str, Any] | None:
        serialized = self._serialize_pending_card_action()
        if serialized is None or self._pending_card_action_choice is None:
            return None
        pending = self._pending_card_action_choice
        serialized["response_required_from_viewer"] = (
            pending.responding_player_index == viewer_index
        )
        serialized["selection_owner"] = (
            "viewer" if pending.selection_owner_index == viewer_index else "opponent"
        )
        return serialized

    def _get_pending_defense_eligible_indices(self) -> list[int]:
        if self._pending_defense_decision is None:
            return []
        defender_owner = self.players[
            self._pending_defense_decision.defending_player_index
        ]
        attacker = self._pending_defense_decision.attacker
        return [
            index
            for index, defender in enumerate(defender_owner.cards_laid_out)
            if self._is_eligible_defender(
                attacker, defender, hunter_target_override=False
            )
        ]

    def _auto_end_turn_after_play_if_needed(self) -> None:
        if not self.auto_end_turn_after_successful_play:
            return
        if self.game_state == GameState.GAME_OVER:
            return
        if self._pending_card_action_choice is not None:
            # Sluggernaut's form choice is queued passively from apply_ongoing_effect
            # and has no inherent auto-end context, so propagate the play context
            # here so the turn ends after the player resolves the choice.
            if self._pending_card_action_choice.action_key == "sluggernaut":
                self._pending_card_action_choice.auto_end_after_play = True
            return
        self.end_turn()

    def _auto_end_turn_after_attack_if_needed(self) -> None:
        if not self.auto_end_turn_after_resolved_attack:
            return
        if self.game_state == GameState.GAME_OVER:
            return
        if self._pending_card_action_choice is not None:
            if self._pending_card_action_choice.action_key == "sluggernaut":
                self._pending_card_action_choice.auto_end_after_attack = True
            return
        if self._pending_defense_decision is not None:
            return
        if self._pending_frenzy_attacker_id is not None:
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
            player.life_loss_before_using_mindbug = 0
            player.cannot_lose_life = False
            player.cannot_play_cards_with_power_4_or_less_from_hand = False
            for card in player.cards_laid_out:
                card.strength = card.base_strength
                card.special_types = list(card.base_special_types)
                card.cannot_block = (
                    card.base_cannot_block or card.temporary_cannot_block_until_turn_end
                )
                card.cannot_attack = card.base_cannot_attack

        # TODO - we must assign apply_ongoing_effect_priority to cards in cards.py to apply ongoing effects in order of priority
        # Jazz_dog should be applied before other cards, because it can give control of other cards to the player
        # Sharky_crab_dog_mummypus should be applied after other cards, because it can give new tags to the card
        all_cards: list[tuple[Card, Any, Any]] = [
            (card, self.players[owner_idx], self.players[1 - owner_idx])
            for owner_idx, owner in enumerate(self.players)
            for card in owner.cards_laid_out
        ]
        for card, owner, opponent in sorted(
            all_cards, key=lambda t: t[0].apply_ongoing_effect_priority
        ):
            card.apply_ongoing_effect(self, owner, opponent)

        self.log.append(f"Ongoing effects recalculated.")
        # NOTE - to handle Multiple Sluggernauts losing TOUGH simultaneously each get their own prompt sequentially.
        # TODO - Is this the right spot? similar to _process_next_hyenix_trigger_if_needed?
        self._process_next_sluggernaut_form_choice_if_needed()
