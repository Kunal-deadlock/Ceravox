import { FormEvent, useState } from "react";

import { login } from "../lib/api";
import type { UserProfile } from "../lib/api";

type LoginProps = { onAuthenticated: (user: UserProfile) => void };

export function Login({ onAuthenticated }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      onAuthenticated(await login(email, password));
    } catch {
      setError("Invalid email or password");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-card" aria-labelledby="login-title">
        <p className="eyebrow">CERAVOX / LOCAL ACCESS</p>
        <h1 id="login-title">Log in to Ceravox</h1>
        <p className="muted">Use the local administrator account to continue.</p>
        <form onSubmit={submit}>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button type="submit" disabled={submitting}>{submitting ? "Logging in…" : "Log in"}</button>
        </form>
      </section>
    </main>
  );
}
