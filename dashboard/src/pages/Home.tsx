import { useEffect, useState } from "react";

import { getHealth, type HealthStatus } from "../lib/api";

export function Home() {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    void getHealth().then(setHealth);
  }, []);

  const statusLabel = health?.status ?? "checking";
  const statusClass = health?.status === "ready" ? "status-ready" : "status-warning";

  return (
    <main className="shell">
      <header className="hero">
        <p className="eyebrow">LOCAL-FIRST VOICE WORKSTATION</p>
        <h1>Ceravox</h1>
        <p className="tagline">Turn spoken thoughts into useful work.</p>
      </header>

      <section className="status-card" aria-live="polite">
        <div>
          <p className="card-label">Backend health</p>
          <h2>{statusLabel === "ready" ? "Ready to listen" : "Backend status"}</h2>
          <p className="muted">
            {statusLabel === "unreachable"
              ? "The backend cannot be reached. Start the API and try again."
              : statusLabel === "not_ready"
                ? "A required local dependency is unavailable."
                : statusLabel === "checking"
                  ? "Checking the local backend…"
                  : "Ceravox is running locally."}
          </p>
        </div>
        <span className={`status-pill ${statusClass}`}>{statusLabel}</span>
      </section>

      <section className="feature-grid" aria-label="Planned workflows">
        <article>
          <span className="feature-number">01</span>
          <h2>Transcribe</h2>
          <p>Convert local audio into timestamped text.</p>
        </article>
        <article>
          <span className="feature-number">02</span>
          <h2>Speak</h2>
          <p>Generate natural speech without a cloud API.</p>
        </article>
        <article>
          <span className="feature-number">03</span>
          <h2>Understand</h2>
          <p>Turn meetings into summaries and action items.</p>
        </article>
      </section>
    </main>
  );
}
