export function getApiBaseUrl(): string {
  const envUrl = (import.meta.env.VITE_API_BASE_URL ?? "").trim().replace(/\/+$/, "");
  try {
    const saved = localStorage.getItem("ceravox_api_url");
    if (saved && saved.trim()) {
      const clean = saved.trim().replace(/\/+$/, "");
      if (clean.includes("trycloudflare.com") && envUrl && !envUrl.includes("trycloudflare.com")) {
        localStorage.removeItem("ceravox_api_url");
        return envUrl;
      }
      return clean;
    }
  } catch {}
  return envUrl;
}

export function setApiBaseUrl(url: string): void {
  try {
    const clean = url.trim().replace(/\/+$/, "");
    if (clean) {
      localStorage.setItem("ceravox_api_url", clean);
    } else {
      localStorage.removeItem("ceravox_api_url");
    }
  } catch {}
}

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem("ceravox_token");
  } catch {
    return null;
  }
}

export function setAuthToken(token: string | null): void {
  try {
    if (token) {
      localStorage.setItem("ceravox_token", token);
    } else {
      localStorage.removeItem("ceravox_token");
    }
  } catch {}
}
