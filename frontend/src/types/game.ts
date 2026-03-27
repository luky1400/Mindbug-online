export type CardLabel = string;
export type CardSet = "First Contact" | "New Servants" | "Promo Cards";

export interface CardPoolEntry {
  label: CardLabel;
  copies: number;
}

export const REQUIRED_CARD_SET: CardSet = "First Contact";
export const CARD_SET_OPTIONS: CardSet[] = [REQUIRED_CARD_SET, "New Servants", "Promo Cards"];

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

export interface PendingCardActionState {
  action_key: string;
  source_card_label: CardLabel;
  responding_player_name: string;
  selection_owner_name: string;
  selection_zone: "hand" | "battlefield" | "discard";
  selection_owner: "viewer" | "opponent";
  response_required_from_viewer: boolean;
  eligible_indices: number[];
  min_choices: number;
  max_choices: number;
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
  pending_card_action: PendingCardActionState | null;
  pending_frenzy_attacker_index: number | null;
  connected_players: number;
  max_players: number;
  invite_code: string;
  selected_sets: CardSet[];
  card_pool_by_set: { [set: string]: CardPoolEntry[] };
}

export interface SessionResponse {
  game_id: string;
  player_id: string;
  state: MultiplayerState;
}

export interface CreateGameRequest {
  player_name: string;
  selected_sets: CardSet[];
}

export interface JoinGameRequest {
  player_name: string;
}

export interface AttackRequest {
  attacker_index: number;
  defender_index: number | null;
}

export interface DefendRequest {
  defender_index: number | null;
}

export interface ResolveCardActionChoiceRequest {
  selected_indices: number[];
}
