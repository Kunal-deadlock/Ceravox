# Ceravox — Hackathon Submission Index

**No Hands: The Wispr Challenge**

## Project

**Ceravox** — A local-first voice AI workstation. Upload audio, get a
transcript, generate meeting notes and action items, ask questions about the
meeting, and hear answers spoken back, all on your own machine with no cloud
dependency after the initial model install.

## 1. Working project / repository link

https://github.com/Kunal-deadlock/Ceravox

Judges: see DEMO.md for exact setup and launch commands.

## 2. Demo video

PENDING — provide the video URL (up to 2 minutes) after recording.

See docs/DEMO_SCRIPT.md for the recording guide.

## 3. Wispr usage-card screenshot

PENDING — export the usage card from Insights in the Wispr Flow desktop app
and attach it here or in the submission form.

## 4. Problem, audience, and Wispr usage

### Problem

Meeting audio is forgotten. People record calls and interviews but rarely
revisit them. Existing transcription and summary tools require cloud accounts,
charge per minute, and send private audio to third-party servers.

### Audience

Students, small teams, journalists, and anyone who wants to turn a recorded
conversation into action items without surrendering their data to a cloud service.

### How Wispr was used

Wispr Flow Pro was the primary development interface throughout Ceravox's build.
It was used to dictate:

- Product specifications and milestone plans
- Architecture decisions and API contracts
- Coding prompts sent to the AI coding assistant
- Code review notes and debugging context
- Commit messages
- This submission copy and demo script

Wispr Flow is a development tool only and is not part of Ceravox's runtime.

## Verified capabilities

- Authenticated audio upload -> local faster-whisper transcript (WAV, MP3, M4A, OGG)
- Persisted, owner-scoped transcript storage and retrieval
- Local Kokoro TTS speech generation and WAV download
- Local Ollama meeting summary and action items (qwen2.5:3b)
- Transcript Q&A (context-in-prompt, no RAG, no cloud)
- Speak Answer: route Q&A result to existing TTS
- Authentication (Argon2id), CSRF, ownership isolation
- Input limits, validation, safe error messages
- Offline operation after model installation

## Known limitations

- Docker Compose runtime is blocked on this machine by a missing Linux engine
  named pipe. Native localhost startup works. Docker config passes.
- Real-time streaming, VAD, barge-in, and voice cloning are deferred (S3).
- Meeting notes latency depends on local hardware (CPU inference on qwen2.5:3b).
- Ollama model (~1.9 GB) and Whisper/Kokoro models (~476 MB) must be installed
  locally before first use. No internet connection is needed after that.
- Single-admin, single-user in this release.

## Final submission checklist

- [x] Repository link supplied and public
- [ ] Demo video recorded and linked (2 minutes max)
- [ ] Wispr usage-card screenshot attached
- [ ] Submission form completed
- [x] No secrets, databases, recordings, or model weights committed
- [x] DEMO.md setup instructions tested end-to-end
