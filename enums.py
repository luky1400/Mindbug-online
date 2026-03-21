from enum import Enum


class CardSpecialType(Enum):
    FRENZY = "FRENZY"
    TOUGH = "TOUGH"
    POISONOUS = "POISONOUS"
    HUNTER = "HUNTER"
    SNEAKY = "SNEAKY"


class CardActionType(Enum):
    PLAY = "PLAY"
    ATTACK = "ATTACK"
    DEFEATED = "DEFEATED"


class CardSet(Enum):
    FIRST_CONTACT = "First Contact"
    NEW_SERVANTS = "New Servants"
    PROMO_CARDS = "Promo Cards"


class GameState(Enum):
    START_TURN = "START_TURN"
    ACTIVE = "ACTIVE"
    AWAITING_MINDBUG = "AWAITING_MINDBUG"
    AWAITING_DEFENSE = "AWAITING_DEFENSE"
    GAME_OVER = "GAME_OVER"