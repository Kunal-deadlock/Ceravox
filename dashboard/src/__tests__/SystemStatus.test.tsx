import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SystemStatus } from "../pages/SystemStatus";

const getSystemStatus = vi.hoisted(() => vi.fn());
vi.mock("../lib/api", () => ({ getSystemStatus }));

describe("SystemStatus", () => {
  it("renders all expected component statuses and overall readiness", async () => {
    getSystemStatus.mockResolvedValue({
      overall: "ready",
      components: {
        db: { status: "ready", reason: "" },
        asr: { status: "ready", reason: "" },
        tts: { status: "ready", reason: "" },
        ollama: { status: "ready", reason: "" },
      },
    });

    render(<SystemStatus />);

    expect(await screen.findByText(/System Status/i)).toBeTruthy();
    expect(screen.getByText(/Overall: ready/i)).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Database" })).toBeTruthy();
    expect(screen.getByText(/Speech-to-Text \(ASR\)/i)).toBeTruthy();
    expect(screen.getByText(/Text-to-Speech \(TTS\)/i)).toBeTruthy();
    expect(screen.getByText(/Local LLM \(Ollama\)/i)).toBeTruthy();
  });

  it("shows unavailable state and reason safely", async () => {
    getSystemStatus.mockResolvedValue({
      overall: "unavailable",
      components: {
        db: { status: "ready", reason: "" },
        asr: { status: "ready", reason: "" },
        tts: { status: "ready", reason: "" },
        ollama: {
          status: "unavailable",
          reason: "Local Ollama is not reachable. Start Ollama and pull qwen2.5:3b.",
        },
      },
    });

    render(<SystemStatus />);

    expect(await screen.findByText(/Overall: unavailable/i)).toBeTruthy();
    expect(
      screen.getByText(/Local Ollama is not reachable. Start Ollama and pull qwen2.5:3b./)
    ).toBeTruthy();
  });

  it("refresh button triggers a new status request", async () => {
    getSystemStatus.mockResolvedValueOnce({
      overall: "unavailable",
      components: {
        db: { status: "ready", reason: "" },
        asr: { status: "unavailable", reason: "Model files are not installed." },
        tts: { status: "ready", reason: "" },
        ollama: { status: "ready", reason: "" },
      },
    });

    render(<SystemStatus />);

    expect(await screen.findByText(/Model files are not installed./)).toBeTruthy();

    getSystemStatus.mockResolvedValueOnce({
      overall: "ready",
      components: {
        db: { status: "ready", reason: "" },
        asr: { status: "ready", reason: "" },
        tts: { status: "ready", reason: "" },
        ollama: { status: "ready", reason: "" },
      },
    });

    const refreshButton = screen.getByRole("button", { name: /Refresh/i });
    fireEvent.click(refreshButton);

    expect(await screen.findByText(/Overall: ready/i)).toBeTruthy();
    expect(getSystemStatus).toHaveBeenCalledTimes(2);
  });

  it("handles backend failure without crashing", async () => {
    getSystemStatus.mockRejectedValue(new Error("Network connection refused"));

    render(<SystemStatus />);

    expect(
      await screen.findByText(/Backend unreachable or error loading system status/i)
    ).toBeTruthy();
    expect(screen.getByText(/Network connection refused/)).toBeTruthy();
  });
});
