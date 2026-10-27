import { useEffect, useState } from "react";
import { getModels, type ModelResponse } from "../lib/api";

export function ModelStatus() {
  const [models, setModels] = useState<ModelResponse | null>(null);
  const [error, setError] = useState("");
  const load = () => void getModels().then(setModels).catch((reason: Error) => setError(reason.message));
  useEffect(load, []);
  if (error) return <section className="status-card" aria-label="Model status"><p role="alert">{error}</p><button type="button" onClick={load}>Retry</button></section>;
  if (!models) return <section className="status-card" aria-label="Model status"><p>Checking local models…</p></section>;
  const entries = [["ASR", models.faster_whisper], ["TTS", models.kokoro]] as const;
  return <section className="status-card" aria-label="Model status"><div><p className="card-label">LOCAL MODEL STATUS</p><div className="model-status-list">{entries.map(([label, model]) => <p key={label}><strong>{label}</strong> {model.model ? `${model.model} — ${model.available ? "available" : "unavailable"}` : model.status}</p>)}</div></div><button type="button" onClick={load}>Refresh</button></section>;
}
