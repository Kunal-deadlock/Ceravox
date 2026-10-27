import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import "@testing-library/jest-dom/vitest";
import { Transcribe } from "../pages/Transcribe";

const api = vi.hoisted(() => ({ transcribeAudio: vi.fn(), getModels: vi.fn(), listTranscripts: vi.fn(), getTranscript: vi.fn() }));
vi.mock("../lib/api", () => api);
beforeEach(() => {
  vi.clearAllMocks();
  api.getModels.mockResolvedValue({ limits: { upload_bytes: 26214400 } });
  api.listTranscripts.mockResolvedValue({ items: [] });
});
it("renders and uploads a selected file, then displays transcript details", async () => {
  api.transcribeAudio.mockResolvedValue({ id: "id", text: "Synthetic sentence", language: "en", duration: 1.2, segments: [{ id: "s", start_ms: 0, end_ms: 1200, text: "Segment text" }] });
  render(<Transcribe />);
  const file = new File(["synthetic"], "test.wav", { type: "audio/wav" });
  fireEvent.change(screen.getByLabelText("Audio file"), { target: { files: [file] } });
  fireEvent.click(screen.getByRole("button", { name: "Transcribe" }));
  expect(await screen.findByText("Synthetic sentence")).toBeTruthy();
  expect(api.transcribeAudio).toHaveBeenCalledWith(file);
  expect(screen.getByText(/en · 1.20 seconds/)).toBeTruthy();
  expect(screen.getByText(/0.00–1.20/)).toBeTruthy();
});
it("rejects invalid files locally", async () => {
  render(<Transcribe />);
  fireEvent.change(screen.getByLabelText("Audio file"), { target: { files: [new File(["x"], "script.exe")] } });
  expect(await screen.findByRole("alert")).toHaveTextContent("WAV, MP3, M4A or OGG");
  expect(api.transcribeAudio).not.toHaveBeenCalled();
});
it("shows model-unavailable errors and allows retry", async () => {
  api.transcribeAudio.mockRejectedValue(new Error("Install the configured local ASR model"));
  render(<Transcribe />);
  fireEvent.change(screen.getByLabelText("Audio file"), { target: { files: [new File(["x"], "test.wav")] } });
  fireEvent.click(screen.getByRole("button", { name: "Transcribe" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("local ASR model");
  await waitFor(() => expect(screen.getByRole("button", { name: "Transcribe" })).not.toBeDisabled());
});
