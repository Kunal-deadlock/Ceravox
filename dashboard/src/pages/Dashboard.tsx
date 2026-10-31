import { NavLink, Outlet } from "react-router-dom";

import type { UserProfile } from "../lib/api";

type DashboardProps = { user: UserProfile; onLogout: () => void };

export function Dashboard({ user, onLogout }: DashboardProps) {
  return (
    <main className="shell app-shell">
      <header className="app-header">
        <div className="brand-wrapper">
          <div className="brand-glyph" aria-hidden="true">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5v14M7 9v6M22 10v4M2 10v4" />
            </svg>
          </div>
          <div>
            <p className="eyebrow">LOCAL-FIRST VOICE WORKSTATION</p>
            <h1>Ceravox dashboard</h1>
          </div>
        </div>
        <div className="account-actions">
          <span className="muted">{user.email}</span>
          <button type="button" className="button-secondary" onClick={onLogout}>
            Log out
          </button>
        </div>
      </header>

      <nav className="app-nav" aria-label="Main navigation">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/transcribe">Transcribe</NavLink>
        <NavLink to="/speak">Speak</NavLink>
        <NavLink to="/live-assistant">Live Assistant</NavLink>
        <NavLink to="/meeting-notes">Meeting Notes</NavLink>
        <NavLink to="/system-status">System Status</NavLink>
      </nav>

      <Outlet />
    </main>
  );
}
