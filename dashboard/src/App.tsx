import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";

import { ApiError, getAuthStatus, getCsrfToken, getMe, logout } from "./lib/api";
import type { UserProfile } from "./lib/api";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { Placeholder } from "./pages/Placeholder";
import { Setup } from "./pages/Setup";
import { Transcribe } from "./pages/Transcribe";
import { Speak } from "./pages/Speak";
import { ModelStatus } from "./components/ModelStatus";

function AuthenticatedRoutes({ user, onLogout }: { user: UserProfile; onLogout: () => void }) {
  return (
    <Routes>
      <Route element={<Dashboard user={user} onLogout={onLogout} />}>
        <Route index element={<><ModelStatus /><section className="status-card"><div><p className="card-label">Private by default</p><h2>Ready for local voice workflows</h2><p className="muted">Transcription and speech stay on this machine after model installation.</p></div><span className="status-pill status-ready">local</span></section></>} />
        <Route path="transcribe" element={<Transcribe />} />
        <Route path="speak" element={<Speak />} />
        <Route path="live-assistant" element={<Placeholder title="Live Assistant" />} />
        <Route path="meeting-notes" element={<Placeholder title="Meeting Notes" />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function isUnauthorized(error: unknown): boolean {
  if (error instanceof ApiError) return error.status === 401;
  return typeof error === "object" && error !== null && "status" in error && error.status === 401;
}

function AppRoutes() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [setupRequired, setSetupRequired] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    void Promise.all([getAuthStatus(), getCsrfToken()])
      .then(async ([status]) => {
        setSetupRequired(status.setup_required);
        if (!status.setup_required) {
          try {
            setUser(await getMe());
          } catch (error) {
            if (!isUnauthorized(error)) throw error;
          }
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <main className="auth-layout"><p className="muted">Checking local access…</p></main>;
  }

  if (setupRequired) {
    return <Routes><Route path="/setup" element={<Setup onComplete={() => { setSetupRequired(false); navigate("/login"); }} />} /><Route path="*" element={<Navigate to="/setup" replace />} /></Routes>;
  }

  if (!user) {
    return <Routes><Route path="/login" element={<Login onAuthenticated={(nextUser) => { setUser(nextUser); navigate("/"); }} />} /><Route path="*" element={<Navigate to="/login" replace />} /></Routes>;
  }

  return <AuthenticatedRoutes user={user} onLogout={async () => { await logout(); setUser(null); navigate("/login"); }} />;
}

export default function App() {
  return <BrowserRouter><AppRoutes /></BrowserRouter>;
}
