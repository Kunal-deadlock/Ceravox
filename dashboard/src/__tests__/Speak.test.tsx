import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import "@testing-library/jest-dom/vitest";
import { Speak } from "../pages/Speak";

const api = vi.hoisted(() => ({ getModels: vi.fn(), generateSpeech: vi.fn() }));
vi.mock("../lib/api", () => api);
beforeEach(() => {
  vi.clearAllMocks();
  api.getModels.mockResolvedValue({ kokoro: { available: true, voices: ["af_heart"], default_voice: "af_heart" }, limits: { text_chars: 2000 } });
  vi.stubGlobal("URL", Object.assign(URL, { createObjectURL: vi.fn(() => "blob:test"), revokeObjectURL: vi.fn() }));
});
it("renders and prevents empty text submission", async () => {
  render(<Speak />);
  await screen.findByRole("option", { name: "af_heart" });
  expect(screen.getByRole("button", { name: "Generate speech" })).toBeDisabled();
  expect(api.generateSpeech).not.toHaveBeenCalled();
});
it("generates playable downloadable audio and cleans object URLs", async () => {
  api.generateSpeech.mockResolvedValue(new Blob(["synthetic"], { type: "audio/wav" }));
  const play = vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();
  const { unmount } = render(<Speak />);
  await screen.findByRole("option", { name: "af_heart" });
  fireEvent.change(screen.getByLabelText("Text to speak"), { target: { value: "Hello" } });
  fireEvent.click(screen.getByRole("button", { name: "Generate speech" }));
  const audio = await screen.findByLabelText("Generated speech");
  expect(audio).toHaveAttribute("src", "blob:test");
  await (audio as HTMLAudioElement).play();
  expect(play).toHaveBeenCalled();
  expect(screen.getByRole("link", { name: "Download WAV" })).toHaveAttribute("href", "blob:test");
  unmount();
  await waitFor(() => expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:test"));
});
