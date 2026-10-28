import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MeetingNotes } from "../pages/MeetingNotes";
import type { MeetingResult } from "../lib/api";

const listTranscripts = vi.hoisted(() => vi.fn());
const getModels = vi.hoisted(() => vi.fn());
const generateSummary = vi.hoisted(() => vi.fn());
const askTranscript = vi.hoisted(() => vi.fn());
const generateSpeech = vi.hoisted(() => vi.fn());

vi.mock("../lib/api", () => ({
  listTranscripts,
  getModels,
  generateSummary,
  askTranscript,
  generateSpeech,
}));

describe("MeetingNotes", () => {
  const fakeTranscript = {
    id: "tx-123",
    created_at: "2026-10-28T12:00:00Z",
    language: "en",
  };

  const setupMocks = () => {
    vi.clearAllMocks();
    listTranscripts.mockResolvedValue({
      items: [fakeTranscript],
      limit: 20,
      offset: 0,
    });
    getModels.mockResolvedValue({
      faster_whisper: { model: "base", available: true, status: "available" },
      kokoro: {
        model: "Kokoro-82M",
        available: true,
        status: "available",
        default_voice: "af_heart",
      },
      ollama: { available: true, status: "available" },
    });
  };

  it("shows loading state and disables buttons while summary is generating", async () => {
    setupMocks();

    let resolveSummary: (val: MeetingResult) => void;
    generateSummary.mockReturnValue(
      new Promise((resolve) => {
        resolveSummary = resolve;
      })
    );

    render(<MeetingNotes />);

    const generateBtn = await screen.findByRole("button", {
      name: /Generate summary and action items/i,
    });
    expect(generateBtn).not.toBeDisabled();

    // Click generate summary
    fireEvent.click(generateBtn);

    // Button should be disabled and show loading state
    expect(generateBtn).toBeDisabled();
    expect(
      screen.getByText(/Generating summary and action items/i)
    ).toBeTruthy();

    // Resolve summary
    resolveSummary!({
      transcript_id: "tx-123",
      kind: "summary",
      text: "Meeting notes summary content.",
    });

    expect(
      await screen.findByText(/Meeting notes summary content./)
    ).toBeTruthy();
    expect(
      screen.getByRole("button", { name: /Generate summary and action items/i })
    ).not.toBeDisabled();
  });

  it("shows loading state while question answer is generating", async () => {
    setupMocks();

    let resolveQuestion: (val: MeetingResult) => void;
    askTranscript.mockReturnValue(
      new Promise((resolve) => {
        resolveQuestion = resolve;
      })
    );

    render(<MeetingNotes />);

    await screen.findByRole("button", {
      name: /Generate summary and action items/i,
    });

    const textarea = screen.getByPlaceholderText(/What decisions were made\?/i);
    fireEvent.change(textarea, { target: { value: "Who is attending?" } });

    const askBtn = screen.getByRole("button", { name: /Ask locally/i });
    expect(askBtn).not.toBeDisabled();

    fireEvent.click(askBtn);

    expect(askBtn).toBeDisabled();
    expect(screen.getByText(/Generating answer from transcript/i)).toBeTruthy();

    resolveQuestion!({
      transcript_id: "tx-123",
      kind: "answer",
      text: "Attendees are Alice and Bob.",
    });

    expect(await screen.findByText(/Attendees are Alice and Bob./)).toBeTruthy();
    expect(screen.getByRole("button", { name: /Speak answer/i })).toBeTruthy();
  });

  it("shows clear error state if Ollama is unavailable or times out", async () => {
    setupMocks();

    generateSummary.mockRejectedValue(
      new Error("Local Ollama or model 'qwen2.5:3b' is unavailable")
    );

    render(<MeetingNotes />);

    const generateBtn = await screen.findByRole("button", {
      name: /Generate summary and action items/i,
    });
    fireEvent.click(generateBtn);

    expect(
      await screen.findByText(
        /Local Ollama or model 'qwen2\.5:3b' is unavailable/
      )
    ).toBeTruthy();
    expect(generateBtn).not.toBeDisabled();
  });

  it("recovers cleanly after retry following an error", async () => {
    setupMocks();

    generateSummary.mockRejectedValueOnce(
      new Error("Local Ollama took too long to respond")
    );

    render(<MeetingNotes />);

    const generateBtn = await screen.findByRole("button", {
      name: /Generate summary and action items/i,
    });
    fireEvent.click(generateBtn);

    expect(
      await screen.findByText(/Local Ollama took too long to respond/)
    ).toBeTruthy();

    // Now mock success for retry
    generateSummary.mockResolvedValueOnce({
      transcript_id: "tx-123",
      kind: "summary",
      text: "Successfully recovered summary.",
    });

    fireEvent.click(generateBtn);

    expect(
      await screen.findByText(/Successfully recovered summary./)
    ).toBeTruthy();
    // Error should be cleared
    expect(
      screen.queryByText(/Local Ollama took too long to respond/)
    ).toBeNull();
  });

  it("prevents duplicate simultaneous requests", async () => {
    setupMocks();

    let resolveSummary: (val: MeetingResult) => void;
    generateSummary.mockReturnValue(
      new Promise((resolve) => {
        resolveSummary = resolve;
      })
    );

    render(<MeetingNotes />);

    const generateBtn = await screen.findByRole("button", {
      name: /Generate summary and action items/i,
    });

    // Rapid double click
    fireEvent.click(generateBtn);
    fireEvent.click(generateBtn);

    expect(generateSummary).toHaveBeenCalledTimes(1);

    resolveSummary!({
      transcript_id: "tx-123",
      kind: "summary",
      text: "Summary text",
    });

    await waitFor(() => {
      expect(generateBtn).not.toBeDisabled();
    });
  });
});
