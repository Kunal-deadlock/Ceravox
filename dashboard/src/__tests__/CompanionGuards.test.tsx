import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Transcribe } from "../pages/Transcribe";
import { Speak } from "../pages/Speak";
import { MeetingNotes } from "../pages/MeetingNotes";

const api = vi.hoisted(() => ({
  getModels: vi.fn(),
  listTranscripts: vi.fn(),
  getTranscript: vi.fn(),
  transcribeAudio: vi.fn(),
  generateSpeech: vi.fn(),
  generateSummary: vi.fn(),
  askTranscript: vi.fn(),
}));

vi.mock("../lib/api", () => api);

describe("Truthful companion capability guards", () => {
  it("Transcribe disables upload button and shows companion notice when faster_whisper is unavailable", async () => {
    api.getModels.mockResolvedValue({
      faster_whisper: { model: "base", available: false, status: "missing_dependency" },
      kokoro: { available: false, status: "missing_dependency" },
      ollama: { available: false, status: "not_configured" },
      limits: { upload_bytes: 26214400, text_chars: 2000, duration_seconds: 600 },
    });
    api.listTranscripts.mockResolvedValue({ items: [] });

    render(<Transcribe />);

    expect(await screen.findByText(/Local Speech-to-Text \(ASR\) not connected/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Transcribe" })).toBeDisabled();
  });

  it("Speak disables generate button and shows companion notice when kokoro is unavailable", async () => {
    api.getModels.mockResolvedValue({
      faster_whisper: { available: false, status: "missing_dependency" },
      kokoro: { model: "Kokoro-82M", available: false, status: "missing_dependency", voices: [] },
      ollama: { available: false, status: "not_configured" },
      limits: { upload_bytes: 26214400, text_chars: 2000, duration_seconds: 600 },
    });

    render(<Speak />);

    expect(await screen.findByText(/Local Text-to-Speech \(TTS\) not connected/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate speech" })).toBeDisabled();
  });

  it("MeetingNotes disables summary and ask buttons when ollama is unavailable", async () => {
    api.getModels.mockResolvedValue({
      faster_whisper: { available: false, status: "missing_dependency" },
      kokoro: { available: false, status: "missing_dependency" },
      ollama: { available: false, status: "not_configured" },
      limits: { upload_bytes: 26214400, text_chars: 2000, duration_seconds: 600 },
    });
    api.listTranscripts.mockResolvedValue({
      items: [{ id: "tx-1", created_at: "2026-10-31T12:00:00Z", language: "en" }],
      limit: 20,
      offset: 0,
    });

    render(<MeetingNotes />);

    expect(await screen.findByText(/Local LLM \(Ollama\) not connected/i)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate summary and action items" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Ask locally" })).toBeDisabled();
  });
});

