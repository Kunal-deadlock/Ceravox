import { useState, useRef, useEffect } from "react";
import { askAssistant, generateSpeech, transcribeAudio } from "../lib/api";
import { AudioRecorder } from "../lib/audioRecorder";

interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  audioUrl?: string;
  timestamp: string;
}

export function LiveAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-1",
      sender: "assistant",
      text: "Hello! I am Ceravox, your local voice AI assistant. Tap 'Start Speaking' or type below to chat offline.",
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

  const recorderRef = useRef<AudioRecorder | null>(null);
  const timerRef = useRef<number | null>(null);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, statusMessage]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (recorderRef.current?.isRecording()) {
        void recorderRef.current.stop();
      }
    };
  }, []);

  const handleSendTextMessage = async () => {
    const text = inputText.trim();
    if (!text || busy) return;
    setInputText("");
    await processUserMessage(text);
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

      await processUserMessage(transcription.text.trim());
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Transcription failed";
      setError(`Voice transcription error: ${msg}`);
      setStatusMessage(null);
      setBusy(false);
    }
  };

  const processUserMessage = async (userText: string) => {
    setError(null);
    setBusy(true);

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: userText,
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
          // Play audio response automatically
          const audio = new Audio(audioUrl);
          void audio.play().catch(() => {
            // Autoplay may be blocked by browser policy until user interacts
          });
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
    <section className="voice-card" style={{ maxWidth: "880px" }} aria-label="Live Assistant">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2>Live Assistant</h2>
          <p className="muted">Offline voice interaction powered by faster-whisper, Qwen2.5, and Kokoro.</p>
        </div>
        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
          <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.85rem", cursor: "pointer", color: "var(--text-secondary)" }}>
            <input
              type="checkbox"
              checked={autoSpeak}
              onChange={(e) => setAutoSpeak(e.target.checked)}
              style={{ width: "auto", margin: 0 }}
            />
            Auto-speak answers
          </label>
          <button type="button" className="button-secondary" onClick={clearChat} disabled={busy || isRecording}>
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="result-card" role="alert" style={{ borderColor: "rgba(239, 68, 68, 0.4)", background: "rgba(239, 68, 68, 0.08)" }}>
          <p className="form-error" style={{ margin: 0 }}>
            {error}
          </p>
        </div>
      )}

      {/* Chat Thread */}
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "14px",
          minHeight: "320px",
          maxHeight: "440px",
          overflowY: "auto",
          padding: "16px",
          borderRadius: "12px",
          background: "var(--bg-input)",
          border: "1px solid var(--border-card)",
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              display: "flex",
              flexDirection: "column",
              alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
              maxWidth: "80%",
            }}
          >
            <div
              style={{
                padding: "12px 16px",
                borderRadius: m.sender === "user" ? "14px 14px 2px 14px" : "14px 14px 14px 2px",
                background:
                  m.sender === "user"
                    ? "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)"
                    : "var(--bg-card-subtle)",
                color: "#f8fafc",
                border: m.sender === "assistant" ? "1px solid var(--border-subtle)" : "none",
                lineHeight: "1.5",
              }}
            >
              <p style={{ margin: 0, fontSize: "0.95rem" }}>{m.text}</p>
              {m.audioUrl && (
                <div style={{ marginTop: "10px" }}>
                  <audio controls src={m.audioUrl} style={{ width: "100%", height: "36px" }}>
                    Your browser does not support audio playback.
                  </audio>
                </div>
              )}
            </div>
            <span
              style={{
                fontSize: "0.72rem",
                color: "var(--text-muted)",
                marginTop: "4px",
                alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              {m.timestamp}
            </span>
          </div>
        ))}

        {statusMessage && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "#38bdf8", fontSize: "0.88rem" }}>
            <span style={{ display: "inline-block", width: "8px", height: "8px", borderRadius: "50%", background: "#38bdf8", animation: "pulse 1.5s infinite" }} />
            {statusMessage}
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Voice and Text Input Area */}
      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {isRecording ? (
            <button
              type="button"
              onClick={stopVoiceRecording}
              style={{
                background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
                color: "#ffffff",
                padding: "12px 20px",
                minWidth: "180px",
              }}
            >
              ⏹ Stop & Send ({recordingSeconds}s)
            </button>
          ) : (
            <button
              type="button"
              onClick={startVoiceRecording}
              disabled={busy}
              style={{
                minWidth: "180px",
              }}
            >
              🎙️ Speak to Assistant
            </button>
          )}

          <input
            type="text"
            placeholder={isRecording ? "Recording audio..." : "Or type a message to the assistant..."}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void handleSendTextMessage();
              }
            }}
            disabled={busy || isRecording}
            style={{ flex: 1, margin: 0 }}
          />

          <button
            type="button"
            onClick={handleSendTextMessage}
            disabled={busy || isRecording || !inputText.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </section>
  );
}

