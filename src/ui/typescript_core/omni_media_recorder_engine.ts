/// <reference lib="dom" />
/// <reference types="node" />
/**
 * OmniMediaRecorderEngine — Production-Grade WebRTC/MediaRecorder Engine
 * ======================================================================
 * Absorbed from: videojs-record
 *
 * Key patterns learned and implemented:
 * - MediaStream / WebRTC capture (audio, video, screen)
 * - MediaRecorder abstraction (chunked Blob harvesting)
 * - MIME type auto-negotiation
 *
 * OMNI Layer: ui/typescript_core
 * @since 2026.4.0
 * @tags ["webrtc", "recording", "videojs-record", "media-stream"]
 */

export interface RecorderError {
  code: string;
  message: string;
  originalError?: any;
}

export class RecorderResult<T> {
  private constructor(
    private readonly _value: T | null,
    private readonly _error: RecorderError | null,
    private readonly _isOk: boolean
  ) {}

  public static ok<T>(value: T): RecorderResult<T> {
    return new RecorderResult<T>(value, null, true);
  }

  public static err<T>(error: RecorderError): RecorderResult<T> {
    return new RecorderResult<T>(null, error, false);
  }

  public get isOk(): boolean { return this._isOk; }
  public get error(): RecorderError | null { return this._error; }
  public unwrap(): T {
    if (!this._isOk || this._error) throw new Error(this._error?.message);
    return this._value as T;
  }
}

export enum RecordType {
  AUDIO_ONLY,
  VIDEO_ONLY,
  AUDIO_VIDEO,
  SCREEN
}

export class OmniMediaRecorderEngine {
  private stream: MediaStream | null = null;
  private recorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private mimeType: string = '';

  constructor() {}

  /** Negotiates optimal MIME type supported by the browser */
  private getSupportedMimeType(type: RecordType): string {
    const videoTypes = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/mp4'];
    const audioTypes = ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4'];

    const targetTypes = type === RecordType.AUDIO_ONLY ? audioTypes : videoTypes;
    
    for (const t of targetTypes) {
      if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(t)) {
        return t;
      }
    }
    return ''; // let browser decide fallback
  }

  /**
   * Initializes capture devices based on RecordType.
   */
  public async initialize(type: RecordType): Promise<RecorderResult<boolean>> {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices) {
      return RecorderResult.err({ code: "DEV_NOT_SUPPORTED", message: "MediaDevices API not supported" });
    }

    try {
      this.chunks = [];
      this.mimeType = this.getSupportedMimeType(type);

      if (type === RecordType.SCREEN) {
        this.stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
      } else {
        const constraints: MediaStreamConstraints = {
          audio: type === RecordType.AUDIO_ONLY || type === RecordType.AUDIO_VIDEO,
          video: type === RecordType.VIDEO_ONLY || type === RecordType.AUDIO_VIDEO
        };
        this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      }

      const options = this.mimeType ? { mimeType: this.mimeType } : undefined;
      this.recorder = new MediaRecorder(this.stream, options);

      this.recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          this.chunks.push(event.data);
        }
      };

      return RecorderResult.ok(true);
    } catch (e: any) {
      return RecorderResult.err({ code: "INIT_FAILED", message: e.message, originalError: e });
    }
  }

  public startRecording(timesliceMs: number = 1000): RecorderResult<boolean> {
    if (!this.recorder) {
      return RecorderResult.err({ code: "RECORDER_MISSING", message: "Initialize not called" });
    }
    if (this.recorder.state === "recording") {
      return RecorderResult.ok(true);
    }

    this.chunks = [];
    this.recorder.start(timesliceMs);
    return RecorderResult.ok(true);
  }

  public stopRecording(): Promise<RecorderResult<Blob>> {
    return new Promise((resolve) => {
      if (!this.recorder || this.recorder.state === "inactive") {
        resolve(RecorderResult.err({ code: "RECORDER_INACTIVE", message: "Not recording" }));
        return;
      }

      this.recorder.onstop = () => {
        const finalBlob = new Blob(this.chunks, { type: this.mimeType });
        resolve(RecorderResult.ok(finalBlob));
      };

      this.recorder.stop();
      if (this.stream) {
        this.stream.getTracks().forEach(t => t.stop());
      }
    });
  }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "RecorderResult",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
