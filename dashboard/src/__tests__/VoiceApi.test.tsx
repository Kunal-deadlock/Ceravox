import { afterEach, expect, it, vi } from "vitest";
import { generateSpeech, transcribeAudio } from "../lib/api";

afterEach(() => vi.unstubAllGlobals());
it("sends credentialed multipart without overriding its boundary", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ csrf_token: "synthetic" })))
    .mockResolvedValueOnce(new Response(JSON.stringify({ id: "id" })));
  vi.stubGlobal("fetch", fetch);
  await transcribeAudio(new File(["x"], "sample.wav"));
  const options = fetch.mock.calls[1][1];
  expect(options.credentials).toBe("include");
  expect(options.body).toBeInstanceOf(FormData);
  expect(options.headers["Content-Type"]).toBeUndefined();
  expect(options.headers["X-CSRF-Token"]).toBe("synthetic");
});
it("consumes binary speech and handles JSON errors", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("WAV", { headers: { "Content-Type": "audio/wav" } })));
  expect(await generateSpeech("Hello", "af_heart")).toBeInstanceOf(Blob);
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ error: { message: "Unavailable" } }), { status: 503 })));
  await expect(generateSpeech("Hello", "af_heart")).rejects.toThrow("Unavailable");
});
