import { Link } from "react-router-dom";
import { ModelStatus } from "./ModelStatus";

export function HomeView() {
  return (
    <div style={{ animation: "fadeInUp 0.35s ease-out forwards" }}>
      {/* ===================================================================
          HERO STAGE (Inspired by izwiai.com - Private Voice & Language AI)
          =================================================================== */}
      <section className="hero-stage" aria-label="Neural Voice Intelligence">
        <div className="hero-content">
          <p className="eyebrow">LOCAL-FIRST PRIVATE VOICE RUNTIME</p>
          <h1>Run private voice and language AI inside your machine.</h1>
          <div className="hero-subtitle-mask">
            Enterprise-grade local voice intelligence with zero cloud calls, complete data privacy, and CPU-optimized inference.
          </div>
        </div>

        {/* Technical Architecture Specs (Izwi style) */}
        <div className="hero-footer">
          <div className="hero-footer-left">
            <p className="eyebrow" style={{ color: "#f97316" }}>Data Boundary</p>
            <p>100% localhost isolated. Audio decoding and speech synthesis never leave your device.</p>
          </div>

          <div className="hero-footer-tags">
            <span className="tech-pill">● Localhost Runtime</span>
            <span className="tech-pill">faster-whisper</span>
            <span className="tech-pill">Kokoro-82M</span>
            <span className="tech-pill">Qwen2.5:3b</span>
            <span className="tech-pill">✦ Wispr Flow Dictation</span>
          </div>
        </div>
      </section>

      {/* ===================================================================
          CORE WORKSTATION MODULES (ASR, TTS, LLM, ASSISTANT)
          =================================================================== */}
      <section className="quick-action-grid" aria-label="Workstation tools">
        <Link to="/live-assistant" className="quick-action-card">
          <div>
            <div className="quick-action-header">
              <span className="eyebrow" style={{ margin: 0 }}>Conversational Runtime</span>
              <div className="soundwave-bars" aria-hidden="true">
                <span className="soundwave-bar" />
                <span className="soundwave-bar" />
                <span className="soundwave-bar" />
                <span className="soundwave-bar" />
                <span className="soundwave-bar" />
              </div>
            </div>
            <h3>Live Assistant</h3>
            <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
              Local voice conversations with offline mic recording, Qwen2.5 LLM, and Kokoro speech.
            </p>
          </div>
          <div style={{ marginTop: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#f97316" }}>Launch Assistant →</span>
            <span className="status-pill status-ready" style={{ fontSize: "0.7rem", padding: "2px 8px" }}>Live</span>
          </div>
        </Link>

        <Link to="/transcribe" className="quick-action-card">
          <div>
            <div className="quick-action-header">
              <span className="eyebrow" style={{ margin: 0 }}>Speech-to-Text</span>
              <span style={{ fontSize: "1.2rem" }}>🎙️</span>
            </div>
            <h3>Transcribe Audio</h3>
            <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
              Convert local audio into timestamped segments, JSON, Markdown, and TXT files.
            </p>
          </div>
          <div style={{ marginTop: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#f97316" }}>Transcribe →</span>
            <span className="tech-pill" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>faster-whisper</span>
          </div>
        </Link>

        <Link to="/speak" className="quick-action-card">
          <div>
            <div className="quick-action-header">
              <span className="eyebrow" style={{ margin: 0 }}>Text-to-Speech</span>
              <span style={{ fontSize: "1.2rem" }}>🔊</span>
            </div>
            <h3>Generate Speech</h3>
            <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
              Synthesize natural audio locally with Kokoro-82M without cloud services.
            </p>
          </div>
          <div style={{ marginTop: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#f97316" }}>Synthesize →</span>
            <span className="tech-pill" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>af_heart</span>
          </div>
        </Link>

        <Link to="/meeting-notes" className="quick-action-card">
          <div>
            <div className="quick-action-header">
              <span className="eyebrow" style={{ margin: 0 }}>Meeting Intelligence</span>
              <span style={{ fontSize: "1.2rem" }}>🧠</span>
            </div>
            <h3>Meeting Notes</h3>
            <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
              Extract summaries, action items, key decisions, and ask conversational questions.
            </p>
          </div>
          <div style={{ marginTop: "16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontSize: "0.82rem", fontWeight: 600, color: "#f97316" }}>Analyze →</span>
            <span className="tech-pill" style={{ fontSize: "0.7rem", padding: "2px 6px" }}>Qwen2.5 3B</span>
          </div>
        </Link>
      </section>

      {/* Model Status Card & Privacy Banner */}
      <ModelStatus />

      <section className="status-card">
        <div>
          <p className="card-label">Private by default</p>
          <h2>Ready for local voice workflows</h2>
          <p className="muted">Transcription and speech stay on this machine after model installation.</p>
        </div>
        <span className="status-pill status-ready">local</span>
      </section>
    </div>
  );
}
