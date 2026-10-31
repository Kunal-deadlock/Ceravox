import { FormEvent, useState } from "react";

import { login, registerUser } from "../lib/api";
import { getApiBaseUrl, setApiBaseUrl } from "../lib/config";
import type { UserProfile } from "../lib/api";

type LoginProps = { onAuthenticated: (user: UserProfile) => void };

export function Login({ onAuthenticated }: LoginProps) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [backendUrl, setBackendUrlState] = useState(getApiBaseUrl());

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (mode === "signup") {
        onAuthenticated(await registerUser(email, password));
      } else {
        onAuthenticated(await login(email, password));
      }
    } catch (err: unknown) {
      if (err instanceof Error && (err.message.includes("Cannot connect") || err.message.includes("Network error"))) {
        setError(err.message);
        setShowConfig(true);
      } else if (mode === "signup") {
        setError(err instanceof Error ? err.message : "Registration failed. Ensure password is at least 12 characters with 3 character types.");
      } else {
        setError("Invalid email or password");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-card" aria-labelledby="login-title">
        <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
          <button
            type="button"
            className={mode === "login" ? "" : "button-secondary"}
            onClick={() => {
              setMode("login");
              setError(null);
            }}
            style={{ flex: 1, padding: "8px 14px", fontSize: "0.85rem" }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={mode === "signup" ? "" : "button-secondary"}
            onClick={() => {
              setMode("signup");
              setError(null);
            }}
            style={{ flex: 1, padding: "8px 14px", fontSize: "0.85rem" }}
          >
            Create Account
          </button>
        </div>

        <p className="eyebrow">CERAVOX / {mode === "signup" ? "NEW ACCOUNT" : "LOCAL ACCESS"}</p>
        <h1 id="login-title">{mode === "signup" ? "Create your Ceravox account" : "Log in to Ceravox"}</h1>
        <p className="muted">
          {mode === "signup"
            ? "Create a local account on this machine. No cloud calls or accounts required."
            : "Use your local account to access your private voice workstation."}
        </p>

        <form onSubmit={submit}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="username"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />

          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            autoComplete={mode === "signup" ? "new-password" : "current-password"}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={mode === "signup" ? 12 : undefined}
          />
          {mode === "signup" && (
            <p className="field-hint" style={{ margin: "2px 0 6px" }}>
              Password must be at least 12 characters and use uppercase, lowercase, numbers, or symbols.
            </p>
          )}

          {error && <p className="form-error" role="alert">{error}</p>}

          <button type="submit" disabled={submitting}>
            {submitting ? (mode === "signup" ? "Creating account…" : "Logging in…") : (mode === "signup" ? "Sign up" : "Log in")}
          </button>
        </form>

        <div style={{ marginTop: "16px", textAlign: "center" }}>
          <button
            type="button"
            className="link-button"
            onClick={() => {
              setMode(mode === "login" ? "signup" : "login");
              setError(null);
            }}
            style={{ fontSize: "0.85rem" }}
          >
            {mode === "login"
              ? "Don't have an account? Sign up here"
              : "Already have an account? Log in here"}
          </button>
        </div>

        <div style={{ marginTop: "20px", padding: "10px 14px", borderRadius: "8px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "#9ca3af" }}>
              Backend: <strong style={{ color: "#d1d5db" }}>{getApiBaseUrl() || "(same-origin)"}</strong>
            </span>
            <button
              type="button"
              className="link-button"
              onClick={() => setShowConfig(!showConfig)}
              style={{ fontSize: "0.75rem" }}
            >
              {showConfig ? "Close" : "Configure API"}
            </button>
          </div>
          {showConfig && (
            <div style={{ marginTop: "8px", display: "flex", gap: "6px" }}>
              <input
                type="text"
                value={backendUrl}
                placeholder="https://your-tunnel.trycloudflare.com"
                onChange={(e) => setBackendUrlState(e.target.value)}
                style={{ flex: 1, fontSize: "0.8rem", padding: "6px 8px" }}
              />
              <button
                type="button"
                onClick={() => {
                  setApiBaseUrl(backendUrl);
                  window.location.reload();
                }}
                style={{ padding: "6px 12px", fontSize: "0.8rem" }}
              >
                Save
              </button>
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
