import { useEffect, useState } from "react";

import { askTranscript, generateSpeech, generateSummary, getModels, listTranscripts } from "../lib/api";
import type { MeetingResult, TranscriptList } from "../lib/api";

type ActiveAction = "summary" | "question" | "speech" | null;

export function MeetingNotes() {
  const [items, setItems] = useState<TranscriptList["items"]>([]);
  const [selected, setSelected] = useState("");
  const [question, setQuestion] = useState("");
  const [summary, setSummary] = useState<MeetingResult | null>(null);
  const [answer, setAnswer] = useState<MeetingResult | null>(null);
  const [audio, setAudio] = useState("");
  const [voice, setVoice] = useState("af_heart");
  const [ollamaAvailable, setOllamaAvailable] = useState<boolean>(true);
  const [action, setAction] = useState<ActiveAction>(null);
  const [error, setError] = useState("");

  const busy = action !== null;

  useEffect(() => {
    void Promise.all([listTranscripts(), getModels()])
      .then(([result, models]) => {
        setItems(result.items);
        if (result.items[0]) setSelected(result.items[0].id);
        if (models.kokoro?.default_voice) setVoice(models.kokoro.default_voice);
        if (models.ollama && models.ollama.available === false) {
          setOllamaAvailable(false);
        }
      })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => () => {
    if (audio) URL.revokeObjectURL(audio);
  }, [audio]);

  async function handleSummary() {
    if (busy || !selected || !ollamaAvailable) return;
    setAction("summary");
    setError("");
    try {
      const result = await generateSummary(selected);
      setSummary(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Local meeting notes failed");
    } finally {
      setAction(null);
    }
  }

  async function handleQuestion() {
    if (busy || !selected || !question.trim() || !ollamaAvailable) return;
    setAction("question");
    setError("");
    try {
      const result = await askTranscript(selected, question.trim());
      setAnswer(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Transcript question failed");
    } finally {
      setAction(null);
    }
  }

  async function handleSpeak() {
    if (busy || !answer) return;
    setAction("speech");
    setError("");
    try {
      const blob = await generateSpeech(answer.text, voice);
      setAudio(URL.createObjectURL(blob));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Speech generation failed");
    } finally {
      setAction(null);
    }
  }

  return (
    <section className="voice-card">
      <h2>Meeting Notes</h2>
      <p className="muted">Summaries and answers use your local Ollama model and saved transcript.</p>

      {!ollamaAvailable && (
        <div className="status-card" style={{ marginTop: "12px", borderLeft: "4px solid #f59e0b" }}>
          <strong>Local LLM (Ollama) not connected</strong>
          <p className="muted" style={{ margin: "4px 0 0", fontSize: "0.85rem" }}>
            Summarization and Q&A require running Ceravox locally with Ollama (qwen2.5:3b).
          </p>
        </div>
      )}

      <label htmlFor="meeting-transcript">Saved transcript</label>
      <select
        id="meeting-transcript"
        value={selected}
        disabled={busy}
        onChange={(event) => {
          setSelected(event.target.value);
          setSummary(null);
          setAnswer(null);
          setAudio("");
          setError("");
        }}
      >
        {items.map((item) => (
          <option key={item.id} value={item.id}>
            {new Date(item.created_at).toLocaleString()} · {item.language ?? "unknown language"}
          </option>
        ))}
      </select>
      {!items.length && (
        <p className="muted">No saved transcripts yet. Upload audio on the Transcribe page first.</p>
      )}

      <button
        type="button"
        disabled={!selected || busy || !ollamaAvailable}
        onClick={() => void handleSummary()}
        title={!ollamaAvailable ? "Meeting notes require running Ceravox locally with Ollama" : undefined}
      >
        {action === "summary" ? "Generating summary…" : "Generate summary and action items"}
      </button>

      {action === "summary" && (
        <p role="status" aria-live="polite" className="muted" style={{ marginTop: "0.5rem" }}>
          Generating summary and action items… this may take 20–60 seconds on CPU.
        </p>
      )}

      {summary && (
        <article className="result-card">
          <h3>Meeting summary and action items</h3>
          <p className="transcript-text">{summary.text}</p>
        </article>
      )}

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem", marginBottom: "6px" }}>
        <label htmlFor="meeting-question" style={{ margin: 0 }}>Ask about this transcript</label>
        <button
          type="button"
          className="button-secondary"
          onClick={() => {
            const el = document.getElementById("meeting-question");
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
          title="Focus question input to dictate using your Wispr Flow desktop hotkey"
        >
          ✦ Dictate with Wispr Flow
        </button>
      </div>
      <textarea
        id="meeting-question"
        rows={3}
        maxLength={2000}
        value={question}
        disabled={busy || !ollamaAvailable}
        onChange={(event) => setQuestion(event.target.value)}
        placeholder="What decisions were made?"
      />

      <button
        type="button"
        disabled={!selected || !question.trim() || busy || !ollamaAvailable}
        onClick={() => void handleQuestion()}
        title={!ollamaAvailable ? "Transcript Q&A requires running Ceravox locally with Ollama" : undefined}
      >
        {action === "question" ? "Asking…" : "Ask locally"}
      </button>

      {action === "question" && (
        <p role="status" aria-live="polite" className="muted" style={{ marginTop: "0.5rem" }}>
          Generating answer from transcript with local Ollama…
        </p>
      )}

      {answer && (
        <article className="result-card">
          <h3>Answer</h3>
          <p className="transcript-text">{answer.text}</p>
          <button
            type="button"
            disabled={busy}
            onClick={() => void handleSpeak()}
          >
            {action === "speech" ? "Generating audio…" : "Speak answer"}
          </button>
          {action === "speech" && (
            <p role="status" aria-live="polite" className="muted" style={{ marginTop: "0.5rem" }}>
              Synthesizing spoken answer with Kokoro…
            </p>
          )}
          {audio && <audio controls aria-label="Spoken answer" src={audio} />}
        </article>
      )}

      {error && (
        <div role="alert" className="result-card" style={{ marginTop: "1rem", borderColor: "#ef4444" }}>
          <p className="form-error" style={{ margin: 0 }}>{error}</p>
        </div>
      )}
    </section>
  );
}
