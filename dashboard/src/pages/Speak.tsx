import { useEffect, useRef, useState } from "react";
import { generateSpeech, getModels } from "../lib/api";

export function Speak() {
  const [text, setText] = useState("");
  const [voices, setVoices] = useState<string[]>([]);
  const [voice, setVoice] = useState("");
  const [limit, setLimit] = useState(2000);
  const [ttsAvailable, setTtsAvailable] = useState<boolean>(true);
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
        if (models.kokoro && models.kokoro.available === false) {
          setTtsAvailable(false);
          setError("Local TTS engine is not configured on this host. Speech generation requires running Ceravox locally with Kokoro-82M.");
        }
      })
      .catch((reason: Error) => setError(reason.message));

    return () => {
      if (audioRef.current) URL.revokeObjectURL(audioRef.current);
    };
  }, []);

  const submit = () => {
    if (!text.trim() || text.length > limit || !voice || !ttsAvailable) return;
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

      {!ttsAvailable && (
        <div className="status-card" style={{ marginTop: "12px", borderLeft: "4px solid #f59e0b" }}>
          <strong>Local Text-to-Speech (TTS) not connected</strong>
          <p className="muted" style={{ margin: "4px 0 0", fontSize: "0.85rem" }}>
            Speech generation requires running Ceravox locally with Kokoro-82M.
          </p>
        </div>
      )}

      <div style={{ marginTop: "8px" }}>
        <label htmlFor="speak-text">Text to speak</label>
        <textarea
          id="speak-text"
          rows={5}
          value={text}
          maxLength={limit}
          disabled={!ttsAvailable}
          onChange={(event) => setText(event.target.value)}
          placeholder="Type or paste text to synthesize into spoken audio..."
        />
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "4px" }}>
          <span className="field-hint">Max {limit} characters. English only.</span>
          <span className="field-hint" style={{ color: text.length > limit * 0.9 ? "#ea580c" : undefined }}>
            {text.length}/{limit}
          </span>
        </div>
      </div>

      <div>
        <label htmlFor="speak-voice">Voice</label>
        <select id="speak-voice" value={voice} disabled={!ttsAvailable} onChange={(event) => setVoice(event.target.value)}>
          {voices.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
      </div>

      <button
        type="button"
        disabled={!text.trim() || text.length > limit || !voice || busy || !ttsAvailable}
        onClick={submit}
        title={!ttsAvailable ? "Speech generation requires running Ceravox locally with Kokoro-82M" : undefined}
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
