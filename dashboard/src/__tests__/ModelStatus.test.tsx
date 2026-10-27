import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { ModelStatus } from "../components/ModelStatus";

const getModels = vi.hoisted(() => vi.fn());
vi.mock("../lib/api", () => ({ getModels }));
it("renders configured model availability", async () => {
  getModels.mockResolvedValue({ faster_whisper: { model: "base", available: true, status: "available" }, kokoro: { model: "Kokoro-82M", available: false, status: "missing_assets" }, ollama: { available: false, status: "not_configured" } });
  render(<ModelStatus />);
  expect(await screen.findByText(/base — available/)).toBeTruthy();
  expect(screen.getByText(/Kokoro-82M — unavailable/)).toBeTruthy();
});
