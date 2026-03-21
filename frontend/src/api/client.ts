import type {
  AttackRequest,
  CreateGameRequest,
  JoinGameRequest,
  SessionResponse
} from "../types/game";
import { io, type Socket } from "socket.io-client";

async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options
    });
  } catch {
    throw new Error("Cannot reach backend API. Start FastAPI on http://127.0.0.1:8000.");
  }

  const raw = await response.text();
  let data: (T & { detail?: string }) | null = null;
  if (raw) {
    try {
      data = JSON.parse(raw) as T & { detail?: string };
    } catch {
      if (!response.ok) {
        throw new Error(`Request failed (${response.status}) and server returned non-JSON response.`);
      }
      throw new Error("Server returned invalid JSON response.");
    }
  }

  if (!response.ok) {
    throw new Error(data?.detail || `Request failed (${response.status}).`);
  }
  if (!data) {
    throw new Error("Server returned empty response.");
  }
  return data;
}

export const gameApi = {
  createGame(payload: CreateGameRequest) {
    return requestJson<SessionResponse>("/game/new", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  joinGame(gameId: string, payload: JoinGameRequest) {
    return requestJson<SessionResponse>(`/game/${gameId}/join`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  getState(gameId: string, playerId: string) {
    return requestJson<SessionResponse>(`/game/${gameId}/state?player_id=${encodeURIComponent(playerId)}`);
  }
};

export interface GameSocketHandlers {
  onState: (response: SessionResponse["state"]) => void;
  onError: (message: string) => void;
}

export function createGameSocket(
  gameId: string,
  playerId: string,
  handlers: GameSocketHandlers
): Socket {
  const socket = io("/", {
    path: "/socket.io",
    transports: ["websocket", "polling"],
    auth: {
      gameId,
      playerId
    }
  });

  socket.on("state_update", (payload: { state: SessionResponse["state"] }) => {
    handlers.onState(payload.state);
  });

  socket.on("action_error", (payload: { message: string }) => {
    handlers.onError(payload.message);
  });

  socket.on("connect_error", (error: Error) => {
    handlers.onError(error.message);
  });

  return socket;
}

export async function emitWithAck<TResponse>(socket: Socket, event: string, payload?: unknown): Promise<TResponse> {
  const response = await socket.emitWithAck(event, payload);
  return response as TResponse;
}

export interface SocketAckResponse {
  ok: boolean;
  error?: string;
}

export const socketActions = {
  requestState(socket: Socket) {
    return emitWithAck<SocketAckResponse>(socket, "request_state");
  },
  playCard(socket: Socket, handIndex: number) {
    return emitWithAck<SocketAckResponse>(socket, "play_card", { hand_index: handIndex });
  },
  attack(socket: Socket, payload: AttackRequest) {
    return emitWithAck<SocketAckResponse>(socket, "attack", payload);
  },
  endTurn(socket: Socket) {
    return emitWithAck<SocketAckResponse>(socket, "end_turn");
  },
  mindbugResponse(socket: Socket, useMindbug: boolean) {
    return emitWithAck<SocketAckResponse>(socket, "mindbug_response", { use_mindbug: useMindbug });
  }
};
