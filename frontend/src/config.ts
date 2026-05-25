const rawServerUrl = import.meta.env.VITE_SERVER_URL?.trim() || "";

export const serverUrl = rawServerUrl || "/";

export function backendUrl(path: string): string {
  if (!rawServerUrl) {
    return path;
  }

  return `${rawServerUrl.replace(/\/+$/, "")}/${path.replace(/^\/+/, "")}`;
}
