import { useEffect, useState } from "react";

import { askTranscript, generateSpeech, generateSummary, getModels, listTranscripts } from "../lib/api";
import type { MeetingResult, TranscriptList } from "../lib/api";

export function MeetingNotes() {
  const [items, setItems] = useState<TranscriptList["items"]>([]);
  const [selected, setSelected] = useState("");
  const [question, setQuestion] = useState("");
  const [summary, setSummary] = useState<MeetingResult | null>(null);
  const [answer, setAnswer] = useState<MeetingResult | null>(null);
  const [audio, setAudio] = useState("");
  const [voice, setVoice] = useState("af_heart");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void Promise.all([listTranscripts(), getModels()]).then(([result, models]) => {
      setItems(result.items);
      if (result.items[0]) setSelected(result.items[0].id);
      if (models.kokoro.default_voice) setVoice(models.kokoro.default_voice);
    }).catch(reason => setError(reason.message));
  }, []);
  useEffect(() => () => { if (audio) URL.revokeObjectURL(audio); }, [audio]);

  async function run(action: () => Promise<MeetingResult>, done: (value: MeetingResult) => void) {
    setBusy(true); setError("");
    try { done(await action()); } catch (reason) { setError(reason instanceof Error ? reason.message : "Local meeting notes failed"); }
    finally { setBusy(false); }
  }

  async function speak() {
    if (!answer) return;
    setBusy(true); setError("");
    try { const blob = await generateSpeech(answer.text, voice); setAudio(URL.createObjectURL(blob)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Speech generation failed"); }
    finally { setBusy(false); }
  }

  return <section className="voice-card">
    <h2>Meeting Notes</h2>
    <p className="muted">Summaries and answers use your local Ollama model and saved transcript.</p>
    <label htmlFor="meeting-transcript">Saved transcript</label>
    <select id="meeting-transcript" value={selected} onChange={event => { setSelected(event.target.value); setSummary(null); setAnswer(null); setAudio(""); }}>
      {items.map(item => <option key={item.id} value={item.id}>{new Date(item.created_at).toLocaleString()} · {item.language ?? "unknown language"}</option>)}
    </select>
    {!items.length && <p className="muted">No saved transcripts yet. Upload audio on the Transcribe page first.</p>}
    <button type="button" disabled={!selected || busy} onClick={() => void run(() => generateSummary(selected), setSummary)}>{busy ? "Working…" : "Generate summary and action items"}</button>
    {summary && <article className="result-card"><h3>Meeting summary and action items</h3><p className="transcript-text">{summary.text}</p></article>}
    <label htmlFor="meeting-question">Ask about this transcript</label>
    <textarea id="meeting-question" rows={3} maxLength={2000} value={question} onChange={event => setQuestion(event.target.value)} placeholder="What decisions were made?" />
    <button type="button" disabled={!selected || !question.trim() || busy} onClick={() => void run(() => askTranscript(selected, question), setAnswer)}>Ask locally</button>
    {answer && <article className="result-card"><h3>Answer</h3><p className="transcript-text">{answer.text}</p><button type="button" disabled={busy} onClick={() => void speak()}>Speak answer</button>{audio && <audio controls aria-label="Spoken answer" src={audio} />}</article>}
    {error && <p role="alert" className="form-error">{error}</p>}
  </section>;
}
