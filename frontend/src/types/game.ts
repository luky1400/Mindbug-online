export type CardLabel = string;

export interface PlayerState {
  player_index: number;
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

export interface PendingMindbugState {
  acting_player_name: string;
  responding_player_name: string;
  card_label: CardLabel;
  response_required_from_viewer: boolean;
}

export interface PendingDefenseState {
  attacking_player_name: string;
  defending_player_name: string;
  attacker_label: CardLabel;
  response_required_from_viewer: boolean;
  eligible_defender_indices: number[];
}

export interface MultiplayerState {
  room_status: string;
  game_state: string;
  turn_player: string | null;
  winner?: string | null;
  log: string[];
  viewer_player_id: string;
  viewer_player_name: string;
  viewer_player_index: number;
  opponent_player_name: string | null;
  is_viewer_turn: boolean;
  viewer: PlayerState | null;
  opponent: PlayerState | null;
  pending_mindbug: PendingMindbugState | null;
  pending_defense: PendingDefenseState | null;
  pending_frenzy_attacker_index: number | null;
  connected_players: number;
  max_players: number;
  invite_code: string;
}

export interface SessionResponse {
  game_id: string;
  player_id: string;
  state: MultiplayerState;
}

export interface CreateGameRequest {
  player_name: string;
}

export interface JoinGameRequest {
  player_name: string;
}

export interface AttackRequest {
  attacker_index: number;
  defender_index: number | null;
  hunter_target_override: boolean;
}

export interface DefendRequest {
  defender_index: number | null;
}
