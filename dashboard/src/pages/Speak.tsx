import { useEffect, useRef, useState } from "react";
import { generateSpeech, getModels } from "../lib/api";

export function Speak() {
  const [text, setText] = useState("");
  const [voices, setVoices] = useState<string[]>([]);
  const [voice, setVoice] = useState("");
  const [limit, setLimit] = useState(2000);
  const [audio, setAudio] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const audioRef = useRef("");

  useEffect(() => {
    void getModels()
      .then((models) => {
        setVoices(models.kokoro.voices ?? []);
        setVoice(models.kokoro.default_voice ?? models.kokoro.voices?.[0] ?? "");
        setLimit(models.limits.text_chars);
        if (!models.kokoro.available) setError("Local TTS model is unavailable.");
      })
      .catch((reason: Error) => setError(reason.message));

    return () => {
      if (audioRef.current) URL.revokeObjectURL(audioRef.current);
    };
  }, []);

  const submit = () => {
    if (!text.trim() || text.length > limit || !voice) return;
    setBusy(true);
    setError("");
    void generateSpeech(text, voice)
      .then((blob) => {
        if (audioRef.current) URL.revokeObjectURL(audioRef.current);
        const url = URL.createObjectURL(blob);
        audioRef.current = url;
        setAudio(url);
      })
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setBusy(false));
  };

  return (
    <section className="voice-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Speak text</h2>
          <p className="muted" style={{ margin: 0 }}>
            Generate natural, emotive speech locally using hexgrad Kokoro-82M.
          </p>
        </div>
        <div className="soundwave-bars" aria-hidden="true">
          <span className="soundwave-bar" />
          <span className="soundwave-bar" />
          <span className="soundwave-bar" />
          <span className="soundwave-bar" />
          <span className="soundwave-bar" />
        </div>
      </div>

      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
          <label htmlFor="speak-text" style={{ margin: 0 }}>Text to speak</label>
          <button
            type="button"
            className="button-secondary"
            onClick={() => {
              const el = document.getElementById("speak-text");
              el?.focus();
            }}
            style={{
              padding: "4px 12px",
              fontSize: "0.75rem",
              borderRadius: "9999px",
              background: "#f0f9ff",
              borderColor: "#bae6fd",
              color: "#0369a1",
            }}
            title="Focus textarea to dictate using your Wispr Flow desktop hotkey"
          >
            ✦ Dictate with Wispr Flow
          </button>
        </div>
        <textarea
          id="speak-text"
          rows={6}
          placeholder="Enter text here or dictate hands-free with Wispr Flow to synthesize into speech..."
          value={text}
          maxLength={limit}
          onChange={(event) => setText(event.target.value)}
        />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px" }}>
          <span className="field-hint" style={{ margin: 0, fontSize: "0.8rem", color: "#64748b" }}>
            💡 Press Wispr Flow hotkey while focused to speak your text.
          </span>
          <span className="field-hint" style={{ margin: 0 }}>
            {text.length} / {limit} characters
          </span>
        </div>
      </div>

      <div>
        <label htmlFor="speak-voice">Voice</label>
        <select id="speak-voice" value={voice} onChange={(event) => setVoice(event.target.value)}>
          {voices.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>

      <button
        type="button"
        disabled={!text.trim() || text.length > limit || !voice || busy}
        onClick={submit}
        style={{ minWidth: "180px", alignSelf: "flex-start" }}
      >
        {busy ? "Generating…" : "Generate speech"}
      </button>

      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}

      {audio && (
        <article className="result-card" style={{ marginTop: "12px", background: "#f8fafc" }}>
          <h3>Generated Audio</h3>
          <audio aria-label="Generated speech" controls src={audio} style={{ width: "100%" }} />
          <div style={{ marginTop: "8px" }}>
            <a
              href={audio}
              download="ceravox-speech.wav"
              className="button-secondary"
              style={{ display: "inline-flex", textDecoration: "none" }}
            >
              Download WAV
            </a>
          </div>
        </article>
      )}
    </section>
  );
}
