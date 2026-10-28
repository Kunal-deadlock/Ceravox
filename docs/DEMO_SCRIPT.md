# Ceravox Demo Script

Recording guide for a two-minute demo video.
Show only implemented, working features.

---

## 0:00–0:15 — Problem and audience

"Most teams record meetings and forget them.
Ceravox turns that audio into transcripts, meeting notes, and spoken answers
entirely on your own hardware — no cloud account, no per-minute billing,
no audio leaves your machine."

---

## 0:15–0:45 — Upload and transcribe

1. Log in to the local Ceravox dashboard (http://127.0.0.1:5173).
2. Navigate to Transcribe.
3. Click "Choose audio file" and select a short WAV or MP3 recording.
4. Click "Transcribe" and wait for the result.
5. Show the transcript text, language, duration, and segment timestamps.
6. Click "Copy", download as TXT, download as JSON.
7. Reload the page to show the transcript persists in the list.

Note: if transcription takes more than a few seconds on your hardware,
speed up that section in editing and add a title card:
"[Whisper base, CPU — real elapsed time sped up x2]"

---

## 0:45–1:20 — Meeting summary and action items

1. Navigate to Meeting Notes.
2. Select the transcript you just saved.
3. Click "Generate summary and action items".
4. Wait for Ollama (qwen2.5:3b, local) to respond.
5. Show the summary and any action items listed.

Note: Ollama CPU inference is slower than cloud services.
If you pre-generate the result for the demo to show the output clearly,
label the cut: "[Result pre-generated with the same local model]"

---

## 1:20–1:45 — Transcript Q&A and spoken answer

1. In the question box, type: "What decisions were made?"
2. Click "Ask locally".
3. Show the answer (generated from the transcript only, no internet).
4. Click "Speak answer" and let the audio control play Kokoro TTS output.

---

## 1:45–1:55 — Wispr development story

"The entire product — specifications, architecture decisions, code prompts,
debug notes, commit messages, and this script — was dictated using Wispr Flow.
Ceravox itself runs offline; Wispr is a development tool only."

Brief cut to Wispr usage-card screenshot from Insights.

---

## 1:55–2:00 — Close

"All AI inference runs locally. No audio leaves this machine.
Ceravox — local-first voice intelligence."

---

## Filming notes

- Keep localhost services running throughout; confirm models loaded before recording.
- Use a short (15–30 s), non-sensitive synthetic recording for the demo.
- Do not show login credentials, real personal audio, or actual session tokens.
- Trim waiting time but label shortened sections honestly.
- Export as MP4, check it plays in a browser before submitting.
