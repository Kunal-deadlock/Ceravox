import { useEffect, useState } from "react";
import { exportTranscript, getModels, getTranscript, listTranscripts, transcribeAudio, type Transcript } from "../lib/api";

const accepted = ["audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4", "audio/x-m4a", "audio/ogg", "application/ogg"];

export function Transcribe() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<Transcript | null>(null);
  const [items, setItems] = useState<Awaited<ReturnType<typeof listTranscripts>>["items"]>([]);
  const [limit, setLimit] = useState(26214400);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void Promise.all([getModels(), listTranscripts()])
      .then(([models, transcripts]) => {
        setLimit(models.limits.upload_bytes);
        setItems(transcripts.items);
      })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  const select = (selected: File | null) => {
    setError("");
    if (!selected) return;
    if (!accepted.includes(selected.type) && !/\.(wav|mp3|m4a|ogg)$/i.test(selected.name)) {
      return setError("Choose WAV, MP3, M4A or OGG audio.");
    }
    if (selected.size > limit) return setError("Audio exceeds the upload limit.");
    setFile(selected);
  };

  const submit = () => {
    if (!file) return;
    setBusy(true);
    setError("");
    void transcribeAudio(file)
      .then(setResult)
      .then(() => listTranscripts().then((data) => setItems(data.items)))
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setBusy(false));
  };

  const download = async (type: "md" | "txt" | "json") => {
    if (!result) return;
    try {
      const blob = await exportTranscript(result.id, type);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `transcript-${result.id}.${type}`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Download failed");
    }
  };

  return (
    <section className="voice-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Transcribe audio</h2>
          <p className="muted" style={{ margin: 0 }}>
            Temporary audio is deleted after processing; transcripts remain private to your account.
          </p>
        </div>
        <span className="tech-pill">faster-whisper</span>
      </div>

      <div style={{ marginTop: "8px" }}>
        <label htmlFor="audio-file">Audio file</label>
        <input
          id="audio-file"
          type="file"
          accept=".wav,.mp3,.m4a,.ogg,audio/*"
          onChange={(event) => select(event.target.files?.[0] ?? null)}
        />
        {file && (
          <p className="field-hint" style={{ marginTop: "6px" }}>
            Selected: <strong>{file.name}</strong> ({(file.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        )}
      </div>

      <button
        type="button"
        disabled={!file || busy}
        onClick={submit}
        style={{ minWidth: "160px", alignSelf: "flex-start" }}
      >
        {busy ? "Transcribing…" : "Transcribe"}
      </button>

      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}

      {result && (
        <article className="result-card" style={{ marginTop: "12px", background: "#f8fafc" }}>
          <h3>Transcript</h3>
          <p className="transcript-text">{result.text || "No speech detected."}</p>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", margin: "6px 0" }}>
            <span className="status-pill status-ready" style={{ fontSize: "0.75rem" }}>
              {result.language ?? "Unknown language"} · {result.duration.toFixed(2)} seconds
            </span>
          </div>

          <h4 style={{ marginTop: "12px" }}>Segments</h4>
          <ol>
            {result.segments.map((segment) => (
              <li key={segment.id}>
                <strong>
                  {(segment.start_ms / 1000).toFixed(2)}–{(segment.end_ms / 1000).toFixed(2)}
                </strong>{" "}
                — {segment.text}
              </li>
            ))}
          </ol>

          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "16px" }}>
            <button type="button" className="button-secondary" onClick={() => void navigator.clipboard.writeText(result.text)}>
              Copy
            </button>
            <button type="button" className="button-secondary" onClick={() => void download("md")}>
              Download MD
            </button>
            <button type="button" className="button-secondary" onClick={() => void download("txt")}>
              Download TXT
            </button>
            <button type="button" className="button-secondary" onClick={() => void download("json")}>
              Download JSON
            </button>
          </div>
        </article>
      )}

      <aside style={{ marginTop: "16px", paddingTop: "16px", borderTop: "1px solid #e2e8f0" }}>
        <h3>Saved transcripts</h3>
        {items.length ? (
          <ul style={{ listStyle: "none", padding: 0, margin: "12px 0 0", display: "grid", gap: "8px" }}>
            {items.map((item) => (
              <li key={item.id}>
                <button
                  type="button"
                  className="link-button"
                  onClick={() => void getTranscript(item.id).then(setResult)}
                  style={{
                    padding: "8px 14px",
                    borderRadius: "10px",
                    background: "#f1f5f9",
                    textDecoration: "none",
                    color: "#0f172a",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "8px",
                  }}
                >
                  📄 {new Date(item.created_at).toLocaleString()}
                </button>
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted" style={{ margin: "6px 0 0" }}>
            No saved transcripts.
          </p>
        )}
      </aside>
    </section>
  );
}
