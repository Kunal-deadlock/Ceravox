import { useEffect, useState } from "react";
import { getSystemStatus } from "../lib/api";
import type { ComponentInfo, ComponentStatus, SystemStatusResponse } from "../lib/api";

const COMPONENT_LABELS: Record<string, string> = {
  db: "Database",
  asr: "Speech-to-Text (ASR)",
  tts: "Text-to-Speech (TTS)",
  ollama: "Local LLM (Ollama)",
};

function statusClass(status: ComponentStatus): string {
  if (status === "ready") return "status-pill status-ready";
  return "status-pill status-pending";
}

export function SystemStatus() {
  const [data, setData] = useState<SystemStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = () => {
    setLoading(true);
    setError("");
    getSystemStatus()
      .then(setData)
      .catch((err: Error) => setError(err.message || "Failed to load status"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    void getSystemStatus()
      .then(setData)
      .catch((err: Error) => setError(err.message || "Failed to load status"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="voice-card" aria-label="System status">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>System Status</h2>
          <p className="muted">Readiness check for local models, database, and inference services.</p>
        </div>
        <button type="button" className="button-secondary" onClick={refresh} disabled={loading}>
          {loading ? "Checking…" : "Refresh"}
        </button>
      </div>

      <div className="status-card" style={{ marginTop: "16px", marginBottom: "16px", borderLeft: "4px solid #3b82f6" }}>
        <p className="card-label">DEPLOYMENT TOPOLOGY</p>
        <h4 style={{ margin: "4px 0 6px" }}>Hosted Data Console & Local Hardware Inference</h4>
        <p className="muted" style={{ margin: 0, fontSize: "0.85rem", lineHeight: 1.5 }}>
          The cloud backend provides persistent PostgreSQL storage, session authentication, and transcript records. Voice transcription (faster-whisper), speech synthesis (Kokoro), and AI assistance (Ollama) run on your local machine with model weights installed.
        </p>
      </div>

      {error && (
        <div className="result-card" role="alert" style={{ marginTop: "1rem" }}>
          <p className="form-error">
            <strong>Backend unreachable or error loading system status:</strong>
          </p>
          <p className="muted">{error}</p>
        </div>
      )}

      {loading && !data && <p className="muted">Querying system status…</p>}

      {data && (
        <div style={{ marginTop: "1rem" }}>
          <div
            className="status-card"
            style={{ marginBottom: "1.5rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}
          >
            <div>
              <p className="card-label">OVERALL SYSTEM READINESS</p>
              <h3>Overall: {data.overall}</h3>
              <p className="muted">
                {data.overall === "ready"
                  ? "All required components are ready for local offline voice workflows."
                  : "Hosted account and database services are active. Voice AI inference requires running the local Ceravox workstation."}
              </p>
            </div>
            <span className={statusClass(data.overall)}>{data.overall}</span>
          </div>

          <div className="status-grid" style={{ display: "grid", gap: "1rem" }}>
            {Object.entries(data.components).map(([key, info]: [string, ComponentInfo]) => (
              <div
                key={key}
                className="result-card"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  margin: 0,
                }}
              >
                <div>
                  <h4 style={{ margin: "0 0 0.25rem 0" }}>{COMPONENT_LABELS[key] ?? key}</h4>
                  <p className="muted" style={{ margin: 0, fontSize: "0.875rem" }}>
                    Component key: <code>{key}</code>
                  </p>
                  {info.reason ? (
                    <p style={{ marginTop: "0.5rem", color: "#d97706", fontSize: "0.875rem" }}>
                      {info.reason}
                    </p>
                  ) : null}
                </div>
                <span className={statusClass(info.status)}>{info.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
