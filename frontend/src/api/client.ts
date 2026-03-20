import type {
  AttackRequest,
  GameResponse,
  PlayCardRequest,
  NewGameRequest
} from "../types/game";

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
  createGame(payload: NewGameRequest) {
    return requestJson<GameResponse>("/game/new", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  getState(gameId: string) {
    return requestJson<GameResponse>(`/game/${gameId}/state`);
  },
  playCard(gameId: string, payload: PlayCardRequest) {
    return requestJson<GameResponse>(`/game/${gameId}/play-card`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  attack(gameId: string, payload: AttackRequest) {
    return requestJson<GameResponse>(`/game/${gameId}/attack`, {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  endTurn(gameId: string) {
    return requestJson<GameResponse>(`/game/${gameId}/end-turn`, {
      method: "POST",
      body: "{}"
    });
  }
};
