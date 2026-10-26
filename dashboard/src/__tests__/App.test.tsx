import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../App";

vi.mock("../lib/api", () => ({
  ApiError: class ApiError extends Error {
    status = 401;
  },
  getAuthStatus: vi.fn().mockResolvedValue({ setup_required: false }),
  getCsrfToken: vi.fn().mockResolvedValue("csrf-token"),
  getMe: vi.fn().mockRejectedValue({ status: 401 }),
}));

describe("App", () => {
  it("renders the login heading", async () => {
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Log in to Ceravox" })).toBeTruthy();
  });
});
