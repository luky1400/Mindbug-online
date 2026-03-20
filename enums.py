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


class GameState(Enum):
    START_TURN = "START_TURN"
    ACTIVE = "ACTIVE"
    GAME_OVER = "GAME_OVER"