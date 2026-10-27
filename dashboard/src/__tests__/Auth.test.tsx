import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

const api = vi.hoisted(() => ({
  getHealth: vi.fn(),
  getAuthStatus: vi.fn(),
  getCsrfToken: vi.fn(),
  getMe: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  setupAdmin: vi.fn(),
  getModels: vi.fn(),
}));

vi.mock("../lib/api", () => api);

describe("S1 authentication shell", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/");
    api.getCsrfToken.mockResolvedValue("csrf-token");
    api.getHealth.mockResolvedValue({ status: "ready", dependencies: {} });
    api.getMe.mockResolvedValue(null);
    api.login.mockResolvedValue({ email: "admin@example.test", is_admin: true });
    api.logout.mockResolvedValue(undefined);
    api.setupAdmin.mockResolvedValue(undefined);
    api.getModels.mockResolvedValue({ faster_whisper: { model: "base", available: true, status: "available" }, kokoro: { model: "Kokoro-82M", available: true, status: "available", voices: ["af_heart"], default_voice: "af_heart" }, ollama: { available: false, status: "not_configured" }, limits: { upload_bytes: 26214400, text_chars: 2000, duration_seconds: 600 } });
    vi.clearAllMocks();
  });

  it("renders the login page when an admin already exists", async () => {
    api.getAuthStatus.mockResolvedValue({ setup_required: false });

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Log in to Ceravox" })).toBeTruthy();
  });

  it("renders first-run setup when no admin exists", async () => {
    api.getAuthStatus.mockResolvedValue({ setup_required: true });

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Create your Ceravox admin" })).toBeTruthy();
  });

  it("renders the authenticated shell after login", async () => {
    api.getAuthStatus.mockResolvedValue({ setup_required: false });
    render(<App />);
    await screen.findByRole("heading", { name: "Log in to Ceravox" });

    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "admin@example.test" } });
    fireEvent.change(screen.getByLabelText("Password"), { target: { value: "Correct-Horse-7!" } });
    fireEvent.click(screen.getByRole("button", { name: "Log in" }));

    expect(await screen.findByRole("heading", { name: "Ceravox dashboard" })).toBeTruthy();
    expect(screen.getByText("admin@example.test")).toBeTruthy();
  });

  it("clears auth state on logout", async () => {
    api.getAuthStatus.mockResolvedValue({ setup_required: false });
    api.getMe.mockResolvedValue({ email: "admin@example.test", is_admin: true });
    render(<App />);
    await screen.findByRole("heading", { name: "Ceravox dashboard" });

    fireEvent.click(screen.getByRole("button", { name: "Log out" }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "Log in to Ceravox" })).toBeTruthy());
  });

  it("redirects to login after a 401 response", async () => {
    api.getAuthStatus.mockResolvedValue({ setup_required: false });
    api.getMe.mockResolvedValue(null);

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Log in to Ceravox" })).toBeTruthy();
  });
});
