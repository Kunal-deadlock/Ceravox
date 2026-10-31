import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";

import { ApiError, getAuthStatus, getCsrfToken, getMe, logout } from "./lib/api";
import { getApiBaseUrl, setApiBaseUrl } from "./lib/config";
import type { UserProfile } from "./lib/api";
import { Dashboard } from "./pages/Dashboard";
import { Login } from "./pages/Login";
import { LiveAssistant } from "./pages/LiveAssistant";
import { Setup } from "./pages/Setup";
import { Transcribe } from "./pages/Transcribe";
import { Speak } from "./pages/Speak";
import { MeetingNotes } from "./pages/MeetingNotes";
import { SystemStatus } from "./pages/SystemStatus";
import { HomeView } from "./components/HomeView";

function AuthenticatedRoutes({ user, onLogout }: { user: UserProfile; onLogout: () => void }) {
  return (
    <Routes>
      <Route element={<Dashboard user={user} onLogout={onLogout} />}>
        <Route index element={<HomeView />} />
        <Route path="transcribe" element={<Transcribe />} />
        <Route path="speak" element={<Speak />} />
        <Route path="live-assistant" element={<LiveAssistant />} />
        <Route path="meeting-notes" element={<MeetingNotes />} />
        <Route path="system-status" element={<SystemStatus />} />
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
  const [networkError, setNetworkError] = useState<string | null>(null);
  const [customUrl, setCustomUrl] = useState(getApiBaseUrl());

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
      .catch((err) => {
        if (err instanceof ApiError && err.status === 0) {
          setNetworkError(err.message);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <main className="auth-layout"><p className="muted">Checking local access…</p></main>;
  }

  if (networkError) {
    return (
      <main className="auth-layout">
        <section className="auth-card" style={{ maxWidth: "460px" }}>
          <p className="eyebrow">BACKEND CONNECTION</p>
          <h1>Connect to Ceravox Backend</h1>
          <p className="muted" style={{ marginBottom: "16px", fontSize: "0.85rem", lineHeight: "1.5" }}>
            The dashboard cannot reach the Ceravox backend API at:
            <br />
            <code style={{ fontSize: "0.8rem", color: "#f97316", wordBreak: "break-all" }}>
              {getApiBaseUrl() || "(same-origin)"}
            </code>
          </p>
          <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
            <input
              type="text"
              value={customUrl}
              placeholder="https://your-tunnel.trycloudflare.com"
              onChange={(e) => setCustomUrl(e.target.value)}
              style={{ flex: 1, padding: "8px 12px", fontSize: "0.85rem" }}
            />
            <button
              type="button"
              onClick={() => {
                setApiBaseUrl(customUrl);
                window.location.reload();
              }}
              style={{ padding: "8px 16px", whiteSpace: "nowrap" }}
            >
              Connect
            </button>
          </div>
          <p className="field-hint" style={{ fontSize: "0.8rem", color: "#6b7280" }}>
            Make sure your Ceravox backend is running locally. Enter your active backend tunnel URL above to connect.
          </p>
        </section>
      </main>
    );
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
