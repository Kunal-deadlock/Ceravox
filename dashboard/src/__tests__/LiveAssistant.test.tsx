import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import "@testing-library/jest-dom/vitest";
import { LiveAssistant } from "../pages/LiveAssistant";

const api = vi.hoisted(() => ({
  askAssistant: vi.fn(),
  generateSpeech: vi.fn(),
  transcribeAudio: vi.fn(),
}));
vi.mock("../lib/api", () => api);

// AudioRecorder is a real class that calls browser APIs — stub it entirely
vi.mock("../lib/audioRecorder", () => ({
  AudioRecorder: vi.fn().mockImplementation(() => ({
    start: vi.fn().mockResolvedValue(undefined),
    stop: vi.fn().mockResolvedValue(new Blob(["audio"], { type: "audio/wav" })),
    isRecording: vi.fn().mockReturnValue(false),
  })),
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal("URL", Object.assign(URL, {
    createObjectURL: vi.fn(() => "blob:test"),
    revokeObjectURL: vi.fn(),
  }));
  // JSDOM does not implement scrollIntoView
  Element.prototype.scrollIntoView = vi.fn();
});

it("renders heading and initial welcome message", () => {
  render(<LiveAssistant />);
  expect(screen.getByRole("region", { name: "Live Assistant" })).toBeInTheDocument();
  expect(screen.getByText(/Hello! I am Ceravox/i)).toBeInTheDocument();
});

it("shows auto-speak checkbox checked by default", () => {
  render(<LiveAssistant />);
  const checkbox = screen.getByRole("checkbox", { name: /auto-speak/i });
  expect(checkbox).toBeChecked();
});

it("Send button is disabled when input is empty", () => {
  render(<LiveAssistant />);
  expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
});

it("displays assistant reply after sending a text message", async () => {
  api.askAssistant.mockResolvedValue({ reply: "I am your offline assistant." });
  api.generateSpeech.mockResolvedValue(new Blob(["speech"], { type: "audio/wav" }));
  vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();

  render(<LiveAssistant />);
  const input = screen.getByPlaceholderText(/type a message/i);
  fireEvent.change(input, { target: { value: "Hello assistant" } });
  expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled();
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() =>
    expect(screen.getByText("I am your offline assistant.")).toBeInTheDocument()
  );
  expect(api.askAssistant).toHaveBeenCalledWith("Hello assistant");
});

it("shows error message when askAssistant rejects", async () => {
  api.askAssistant.mockRejectedValue(new Error("Ollama timeout"));
  render(<LiveAssistant />);
  const input = screen.getByPlaceholderText(/type a message/i);
  fireEvent.change(input, { target: { value: "Will this fail?" } });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));

  await waitFor(() =>
    expect(screen.getByRole("alert")).toBeInTheDocument()
  );
  expect(screen.getByText(/Ollama timeout/i)).toBeInTheDocument();
});
