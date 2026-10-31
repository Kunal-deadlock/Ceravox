import { useState, useRef, useEffect } from "react";
import { askAssistant, generateSpeech, transcribeAudio, getModels } from "../lib/api";
import { AudioRecorder } from "../lib/audioRecorder";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  audioUrl?: string;
  timestamp: string;
  source?: "wispr-flow" | "mic-whisper";
}

export function LiveAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-1",
      sender: "assistant",
      text: "Hello! I am Ceravox, your local voice AI assistant. Tap 'Speak to Assistant' for offline mic recording, or dictate hands-free with Wispr Flow below.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [assistantAvailable, setAssistantAvailable] = useState(true);

  const recorderRef = useRef<AudioRecorder | null>(null);
  const timerRef = useRef<number | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, statusMessage]);

  useEffect(() => {
    void getModels()
      .then((models) => {
        if (models.ollama && models.ollama.available === false) {
          setAssistantAvailable(false);
        }
      })
      .catch(() => {
        /* ignore */
      });

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (recorderRef.current?.isRecording()) {
        void recorderRef.current.stop();
      }
    };
  }, []);

  const handleSendTextMessage = async (source: "wispr-flow" | "mic-whisper" = "wispr-flow") => {
    const text = inputText.trim();
    if (!text || busy) return;
    setInputText("");
    await processUserMessage(text, source);
  };

  const startVoiceRecording = async () => {
    setError(null);
    try {
      if (!recorderRef.current) {
        recorderRef.current = new AudioRecorder();
      }
      await recorderRef.current.start();
      setIsRecording(true);
      setRecordingSeconds(0);
      timerRef.current = window.setInterval(() => {
        setRecordingSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Microphone access denied";
      setError(`Microphone error: ${msg}. Make sure microphone permissions are granted.`);
    }
  };

  const stopVoiceRecording = async () => {
    if (!recorderRef.current || !isRecording) return;
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setIsRecording(false);
    setStatusMessage("Processing speech with faster-whisper...");
    setBusy(true);

    try {
      const wavBlob = await recorderRef.current.stop();
      if (wavBlob.size < 500) {
        setStatusMessage(null);
        setBusy(false);
        setError("Audio was too short or empty. Please speak clearly into your microphone.");
        return;
      }

      const audioFile = new File([wavBlob], "assistant_voice.wav", { type: "audio/wav" });
      const transcription = await transcribeAudio(audioFile);

      if (!transcription.text || !transcription.text.trim()) {
        setStatusMessage(null);
        setBusy(false);
        setError("Could not detect any speech in the recording. Try again.");
        return;
      }

      await processUserMessage(transcription.text.trim(), "mic-whisper");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Transcription failed";
      setError(`Voice transcription error: ${msg}`);
      setStatusMessage(null);
      setBusy(false);
    }
  };

  const processUserMessage = async (userText: string, source: "wispr-flow" | "mic-whisper" = "wispr-flow") => {
    setError(null);
    setBusy(true);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: userText,
      source,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setStatusMessage("Generating response with local Ollama (qwen2.5:3b)...");

    try {
      const { reply } = await askAssistant(userText);
      let audioUrl: string | undefined = undefined;

      if (autoSpeak) {
        setStatusMessage("Synthesizing voice response with Kokoro-82M...");
        try {
          const speechBlob = await generateSpeech(reply, "af_heart");
          audioUrl = URL.createObjectURL(speechBlob);
          const audio = new Audio(audioUrl);
          void audio.play().catch(() => {});
        } catch {
          // Fallback: speech synthesis failed, but text response still valid
        }
      }

      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: "assistant",
        text: reply,
        audioUrl,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Assistant request failed";
      setError(`Assistant error: ${msg}`);
    } finally {
      setStatusMessage(null);
      setBusy(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome-reset",
        sender: "assistant",
        text: "Conversation cleared. How can I help you?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setError(null);
  };

  return (
    <section className="voice-card" style={{ maxWidth: "920px" }} aria-label="Live Assistant">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "12px" }}>
        <div>
          <h2>Live Assistant</h2>
          <p className="muted" style={{ margin: 0 }}>
            Offline voice interaction powered by faster-whisper, Qwen2.5, and Kokoro.
          </p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center", flexWrap: "wrap" }}>
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              fontSize: "0.86rem",
              fontWeight: 500,
              cursor: "pointer",
              color: "#475569",
              margin: 0,
              padding: "6px 12px",
              borderRadius: "9999px",
              background: "#f1f5f9",
              border: "1px solid #e2e8f0",
            }}
          >
            <input
              type="checkbox"
              checked={autoSpeak}
              onChange={(e) => setAutoSpeak(e.target.checked)}
              style={{ width: "auto", margin: 0, cursor: "pointer" }}
            />
            Auto-speak answers
          </label>
          <button type="button" className="button-secondary" onClick={clearChat} disabled={busy || isRecording || !assistantAvailable}>
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="result-card" role="alert" style={{ borderColor: "#fca5a5", background: "#fef2f2", margin: 0 }}>
          <p className="form-error" style={{ margin: 0 }}>
            {error}
          </p>
        </div>
      )}

      {!assistantAvailable && (
        <div className="status-card" style={{ marginBottom: "16px", borderLeft: "4px solid #f59e0b" }}>
          <strong>Local Voice AI not connected</strong>
          <p className="muted" style={{ margin: "4px 0 0", fontSize: "0.85rem" }}>
            The live assistant requires running Ceravox locally with Ollama (qwen2.5:3b) and Whisper. Real-time AI responses require your local runtime.
          </p>
        </div>
      )}

      {/* Chat Thread */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          minHeight: "360px",
          maxHeight: "480px",
          overflowY: "auto",
          padding: "24px",
          borderRadius: "20px",
          background: "#f8fafc",
          border: "1px solid #e2e8f0",
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              display: "flex",
              flexDirection: "column",
              alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
              maxWidth: "82%",
              animation: "fadeInUp 0.25s ease-out forwards",
            }}
          >
            <div
              style={{
                padding: "14px 18px",
                borderRadius: m.sender === "user" ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
                background: m.sender === "user" ? "#0f172a" : "#ffffff",
                color: m.sender === "user" ? "#ffffff" : "#0f172a",
                border: m.sender === "assistant" ? "1px solid #e2e8f0" : "none",
                boxShadow: m.sender === "assistant" ? "0 2px 8px rgba(0,0,0,0.03)" : "0 4px 12px rgba(15, 23, 42, 0.15)",
                lineHeight: "1.55",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px", marginBottom: "4px" }}>
                {m.source === "wispr-flow" && (
                  <span
                    style={{
                      fontSize: "0.68rem",
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: "9999px",
                      background: "rgba(56, 189, 248, 0.2)",
                      color: "#38bdf8",
                      border: "1px solid rgba(56, 189, 248, 0.4)",
                    }}
                  >
                    ✦ Dictated with Wispr Flow
                  </span>
                )}
                {m.source === "mic-whisper" && (
                  <span
                    style={{
                      fontSize: "0.68rem",
                      fontWeight: 600,
                      padding: "2px 8px",
                      borderRadius: "9999px",
                      background: "rgba(16, 185, 129, 0.2)",
                      color: "#34d399",
                      border: "1px solid rgba(52, 211, 153, 0.4)",
                    }}
                  >
                    🎙️ Mic · faster-whisper
                  </span>
                )}
              </div>
              <p style={{ margin: 0, fontSize: "0.95rem" }}>{m.text}</p>
              {m.audioUrl && (
                <div style={{ marginTop: "12px" }}>
                  <audio controls src={m.audioUrl} style={{ width: "100%", height: "36px" }}>
                    Your browser does not support audio playback.
                  </audio>
                </div>
              )}
            </div>
            <span
              style={{
                fontSize: "0.72rem",
                color: "#94a3b8",
                marginTop: "4px",
                padding: "0 4px",
                alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              {m.timestamp}
            </span>
          </div>
        ))}

        {statusMessage && (
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "10px",
              color: "#0f172a",
              fontSize: "0.88rem",
              fontWeight: 500,
              padding: "8px 16px",
              borderRadius: "9999px",
              background: "#ffffff",
              border: "1px solid #e2e8f0",
              alignSelf: "flex-start",
              boxShadow: "0 2px 6px rgba(0,0,0,0.04)",
            }}
          >
            <div className="soundwave-bars" aria-hidden="true">
              <span className="soundwave-bar" />
              <span className="soundwave-bar" />
              <span className="soundwave-bar" />
            </div>
            {statusMessage}
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Voice and Text Input Area with Wispr Flow integration */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
          {isRecording ? (
            <button
              type="button"
              onClick={stopVoiceRecording}
              style={{
                background: "#dc2626",
                color: "#ffffff",
                padding: "12px 22px",
                minWidth: "200px",
                animation: "ripplePulse 1.5s infinite",
              }}
            >
              ⏹ Stop & Send ({recordingSeconds}s)
            </button>
          ) : (
            <button
              type="button"
              onClick={startVoiceRecording}
              disabled={busy || !assistantAvailable}
              style={{
                minWidth: "200px",
                background: "#0f172a",
              }}
            >
              🎙️ Speak to Assistant
            </button>
          )}

          <div style={{ flex: 1, display: "flex", position: "relative", minWidth: "240px" }}>
            <input
              ref={inputRef}
              type="text"
              placeholder={isRecording ? "Recording voice audio..." : "Type a message or dictate with Wispr Flow hotkey..."}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onInput={(e) => setInputText((e.target as HTMLInputElement).value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void handleSendTextMessage("wispr-flow");
                }
              }}
              disabled={busy || isRecording || !assistantAvailable}
              style={{ flex: 1, margin: 0, paddingRight: "140px" }}
            />
            <button
              type="button"
              className="button-secondary"
              onClick={() => inputRef.current?.focus()}
              title="Click to focus and press Wispr Flow desktop hotkey"
              style={{
                position: "absolute",
                right: "6px",
                top: "50%",
                transform: "translateY(-50%)",
                padding: "4px 10px",
                fontSize: "0.75rem",
                borderRadius: "9999px",
                background: "#f0f9ff",
                borderColor: "#bae6fd",
                color: "#0369a1",
              }}
            >
              ✦ Wispr Flow
            </button>
          </div>

          <button
            type="button"
            onClick={() => void handleSendTextMessage("wispr-flow")}
            disabled={busy || isRecording || !inputText.trim() || !assistantAvailable}
          >
            Send
          </button>
        </div>

        <p className="field-hint" style={{ margin: "2px 0 0", fontSize: "0.82rem", color: "#64748b" }}>
          💡 <strong>Wispr Flow Pro Dictation:</strong> Focus the input and press your Wispr Flow desktop hotkey to dictate hands-free.
        </p>
      </div>
    </section>
  );
}
