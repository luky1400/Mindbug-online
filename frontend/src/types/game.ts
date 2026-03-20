export type CardLabel = string;

export interface PlayerState {
  name: string;
  lives: number;
  mindbugs_remaining: number;
  hand_count: number;
  draw_count: number;
  discard_count: number;
  battlefield: CardLabel[];
  discard: CardLabel[];
  hand?: CardLabel[];
}

export interface GameState {
  turn_player: string;
  game_state: string;
  winner?: string | null;
  log: string[];
  players: PlayerState[];
  turn_hand?: CardLabel[];
}

export interface GameResponse {
  game_id: string;
  state: GameState;
}

export interface NewGameRequest {
  player1: string;
  player2: string;
}

export interface PlayCardRequest {
  hand_index: number;
  use_opponent_mindbug: boolean;
}

export interface AttackRequest {
  attacker_index: number;
  defender_index: number | null;
  hunter_target_override: boolean;
}
