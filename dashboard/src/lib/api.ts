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

export type ModelStatus = { model?: string | null; configured?: boolean; available: boolean; status: string; voices?: string[]; default_voice?: string | null };
export type ModelResponse = { faster_whisper: ModelStatus; kokoro: ModelStatus; ollama: ModelStatus; limits: { upload_bytes: number; text_chars: number; duration_seconds: number; response_formats?: string[] } };
export type TranscriptSegment = { id: string; start_ms: number; end_ms: number; text: string };
export type Transcript = { id: string; storage_id: string; source_type: string; text: string; language: string | null; duration: number; created_at: string; segments: TranscriptSegment[] };
export type TranscriptList = { items: Omit<Transcript, "text" | "segments">[]; limit: number; offset: number };
export type MeetingResult = { transcript_id: string; kind: "summary" | "answer"; text: string };

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
  const isForm = options.body instanceof FormData;
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      ...(isForm ? {} : { "Content-Type": "application/json" }),
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

async function binaryRequest(path: string, options: RequestInit = {}): Promise<Blob> {
  const response = await fetch(`${apiBaseUrl}${path}`, { ...options, credentials: "include", headers: { "Content-Type": "application/json", ...(options.headers ?? {}) } });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new ApiError(payload?.error?.message ?? "Request failed", response.status);
  }
  return response.blob();
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

export async function getModels(): Promise<ModelResponse> { return request<ModelResponse>("/v1/models"); }
export async function transcribeAudio(file: File): Promise<Transcript> {
  const token = await csrfHeaders();
  const form = new FormData(); form.append("file", file);
  return request<Transcript>("/v1/audio/transcriptions", { method: "POST", headers: token, body: form });
}
export async function listTranscripts(): Promise<TranscriptList> { return request<TranscriptList>("/v1/transcripts"); }
export async function getTranscript(id: string): Promise<Transcript> { return request<Transcript>(`/v1/transcripts/${encodeURIComponent(id)}`); }
export async function generateSpeech(text: string, voice: string): Promise<Blob> {
  return binaryRequest("/v1/audio/speech", { method: "POST", headers: await csrfHeaders(), body: JSON.stringify({ text, voice, response_format: "wav" }) });
}
export async function generateSummary(id: string): Promise<MeetingResult> {
  return request<MeetingResult>(`/v1/transcripts/${encodeURIComponent(id)}/summary`, { method: "POST", headers: await csrfHeaders(), body: "{}" });
}
export async function askTranscript(id: string, question: string): Promise<MeetingResult> {
  return request<MeetingResult>(`/v1/transcripts/${encodeURIComponent(id)}/questions`, { method: "POST", headers: await csrfHeaders(), body: JSON.stringify({ question }) });
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
