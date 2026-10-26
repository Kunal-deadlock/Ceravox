export type HealthStatus = {
  status: "ready" | "not_ready" | "unreachable";
  dependencies: Record<string, "available" | "unavailable">;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

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
