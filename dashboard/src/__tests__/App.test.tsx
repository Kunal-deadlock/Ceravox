import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

vi.mock("../lib/api", () => ({
  getHealth: vi.fn().mockResolvedValue({ status: "ready", dependencies: {} }),
}));

describe("App", () => {
  beforeEach(() => vi.clearAllMocks());

  it("renders the Ceravox heading", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Ceravox" })).toBeTruthy();
    expect(await screen.findByText("Ready to listen")).toBeTruthy();
  });
});
