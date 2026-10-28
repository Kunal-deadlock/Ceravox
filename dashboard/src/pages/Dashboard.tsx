import { NavLink, Outlet } from "react-router-dom";

import type { UserProfile } from "../lib/api";

type DashboardProps = { user: UserProfile; onLogout: () => void };

export function Dashboard({ user, onLogout }: DashboardProps) {
  return (
    <main className="shell app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">LOCAL-FIRST VOICE WORKSTATION</p>
          <h1>Ceravox dashboard</h1>
        </div>
        <div className="account-actions">
          <span className="muted">{user.email}</span>
          {user.is_admin && <span className="status-pill status-ready">admin</span>}
          <button type="button" className="button-secondary" onClick={onLogout}>Log out</button>
        </div>
      </header>
      <nav className="app-nav" aria-label="Main navigation">
        <NavLink to="/">Home</NavLink>
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
