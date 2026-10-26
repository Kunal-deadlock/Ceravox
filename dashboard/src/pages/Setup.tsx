import { FormEvent, useState } from "react";

import { setupAdmin } from "../lib/api";

type SetupProps = { onComplete: () => void };

export function Setup({ onComplete }: SetupProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await setupAdmin(email, password);
      onComplete();
    } catch {
      setError("Admin setup could not be completed. Check the password and try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-layout">
      <section className="auth-card" aria-labelledby="setup-title">
        <p className="eyebrow">CERAVOX / FIRST RUN</p>
        <h1 id="setup-title">Create your Ceravox admin</h1>
        <p className="muted">This one-time account stays on this local machine.</p>
        <form onSubmit={submit}>
          <label htmlFor="setup-email">Email</label>
          <input id="setup-email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <label htmlFor="setup-password">Password</label>
          <input id="setup-password" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={12} required />
          <p className="field-hint">Use at least 12 characters with three character types.</p>
          {error && <p className="form-error" role="alert">{error}</p>}
          <button type="submit" disabled={submitting}>{submitting ? "Creating admin…" : "Create admin"}</button>
        </form>
      </section>
    </main>
  );
}
