export type HealthStatus = {
  status: "ready" | "not_ready" | "unreachable";
  dependencies: Record<string, "available" | "unavailable">;
};

export type UserProfile = {
  id: string;
  email: string;
  is_admin: boolean;
};

export type AuthStatus = {
  setup_required: boolean;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
let csrfToken: string | null = null;

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as
      | { error?: { message?: string } }
      | null;
    throw new ApiError(payload?.error?.message ?? "Request failed", response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

async function csrfHeaders(): Promise<Record<string, string>> {
  if (!csrfToken) {
    csrfToken = await getCsrfToken();
  }
  return { "X-CSRF-Token": csrfToken };
}

export async function getHealth(): Promise<HealthStatus> {
  try {
    const response = await fetch(`${apiBaseUrl}/health/ready`);
    const payload = (await response.json()) as Partial<HealthStatus>;
    if (!response.ok) {
      return {
        status: "not_ready",
        dependencies: payload.dependencies ?? {},
      };
    }
    return {
      status: payload.status === "ready" ? "ready" : "not_ready",
      dependencies: payload.dependencies ?? {},
    };
  } catch {
    return { status: "unreachable", dependencies: {} };
  }
}

export function getAuthStatus(): Promise<AuthStatus> {
  return request<AuthStatus>("/v1/auth/status");
}

export async function getCsrfToken(): Promise<string> {
  const payload = await request<{ csrf_token: string }>("/v1/auth/csrf");
  csrfToken = payload.csrf_token;
  return csrfToken;
}

export function getMe(): Promise<UserProfile> {
  return request<UserProfile>("/v1/auth/me");
}

export async function setupAdmin(email: string, password: string): Promise<UserProfile> {
  return request<UserProfile>("/v1/auth/setup", {
    method: "POST",
    headers: await csrfHeaders(),
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string): Promise<UserProfile> {
  return request<UserProfile>("/v1/auth/login", {
    method: "POST",
    headers: await csrfHeaders(),
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<void> {
  await request<void>("/v1/auth/logout", {
    method: "POST",
    headers: await csrfHeaders(),
  });
  csrfToken = null;
}
