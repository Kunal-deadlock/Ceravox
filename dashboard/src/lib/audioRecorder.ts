/**
 * In-browser 16 kHz Mono WAV audio recorder using standard Web Audio API.
 * Free of external dependencies, works across all standard browsers.
 */

export class AudioRecorder {
  private stream: MediaStream | null = null;
  private audioContext: AudioContext | null = null;
  private processor: ScriptProcessorNode | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private audioChunks: Float32Array[] = [];
  private recording = false;

  async start(): Promise<void> {
    this.audioChunks = [];
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        echoCancellation: true,
        noiseSuppression: true,
      },
    });

    const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    this.audioContext = new AudioContextClass({ sampleRate: 16000 });
    this.source = this.audioContext.createMediaStreamSource(this.stream);

    // 4096 sample buffer size for balanced latency and performance
    this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
    this.processor.onaudioprocess = (event: AudioProcessingEvent) => {
      if (!this.recording) return;
      const channelData = event.inputBuffer.getChannelData(0);
      this.audioChunks.push(new Float32Array(channelData));
    };

    this.source.connect(this.processor);
    this.processor.connect(this.audioContext.destination);
    this.recording = true;
  }

  async stop(): Promise<Blob> {
    this.recording = false;

    if (this.source && this.processor) {
      this.source.disconnect();
      this.processor.disconnect();
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }

    if (this.audioContext && this.audioContext.state !== "closed") {
      await this.audioContext.close();
      this.audioContext = null;
    }

    return this.exportWav();
  }

  isRecording(): boolean {
    return this.recording;
  }

  private exportWav(): Blob {
    // Merge chunks
    const totalLength = this.audioChunks.reduce((acc, chunk) => acc + chunk.length, 0);
    const merged = new Float32Array(totalLength);
    let offset = 0;
    for (const chunk of this.audioChunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }

    // Convert Float32 (-1.0 to 1.0) to 16-bit PCM Int16
    const pcmData = new Int16Array(totalLength);
    for (let i = 0; i < totalLength; i++) {
      const s = Math.max(-1, Math.min(1, merged[i]));
      pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
    }

    // 44-byte standard RIFF WAV header
    const buffer = new ArrayBuffer(44 + pcmData.byteLength);
    const view = new DataView(buffer);

    const writeString = (view: DataView, offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(view, 0, "RIFF");
    view.setUint32(4, 36 + pcmData.byteLength, true);
    writeString(view, 8, "WAVE");
    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true); // PCM chunk size
    view.setUint16(20, 1, true); // Linear quantization (PCM)
    view.setUint16(22, 1, true); // 1 Channel (Mono)
    view.setUint32(24, 16000, true); // Sample rate: 16 kHz
    view.setUint32(28, 16000 * 2, true); // Byte rate (SampleRate * ChannelCount * BitsPerSample / 8)
    view.setUint16(32, 2, true); // Block align (ChannelCount * BitsPerSample / 8)
    view.setUint16(34, 16, true); // Bits per sample
    writeString(view, 36, "data");
    view.setUint32(40, pcmData.byteLength, true);

    // Write PCM samples into buffer
    const pcmView = new Int16Array(buffer, 44);
    pcmView.set(pcmData);

    return new Blob([buffer], { type: "audio/wav" });
  }
}
