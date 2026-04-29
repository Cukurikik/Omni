/// <reference lib="dom" />
/// <reference types="node" />
/**
 * OmniDrumSequencerEngine — Production-Grade Web Sequencer 
 * ========================================================
 * Absorbed from: hydrogen
 *
 * Key patterns learned and implemented:
 * - Deterministic grid scheduling (1/16th note arrays)
 * - Look-ahead Web Audio scheduling (avoiding JS thread lag)
 * - Micro-timing (Swing offset calculations)
 *
 * OMNI Layer: ui/typescript_core
 * @since 2026.4.0
 * @tags ["audio", "sequencer", "hydrogen", "rhythm"]
 */

export interface SeqError {
  code: string;
  message: string;
}

export class SeqResult<T> {
  private constructor(
    private readonly _value: T | null,
    private readonly _error: SeqError | null,
    private readonly _isOk: boolean
  ) {}

  public static ok<T>(value: T): SeqResult<T> { return new SeqResult<T>(value, null, true); }
  public static err<T>(error: SeqError): SeqResult<T> { return new SeqResult<T>(null, error, false); }
  public get isOk(): boolean { return this._isOk; }
  public unwrap(): T {
    if (!this._isOk || this._error) throw new Error(this._error?.message);
    return this._value as T;
  }
}

export interface DrumHit {
  velocity: number; // 0.0 - 1.0 (0 = rest)
}

export interface InstrumentTrack {
  id: string;
  name: string;
  buffer: AudioBuffer | null;
  pattern: DrumHit[]; // typically 16 steps
}

export class OmniDrumSequencerEngine {
  private ctx: AudioContext | null = null;
  private tracks: Map<string, InstrumentTrack> = new Map();
  
  private bpm: number = 120;
  private isPlaying: boolean = false;
  private currentStep: number = 0;
  private nextNoteTime: number = 0.0;
  private scheduleAheadTime: number = 0.1; // 100ms
  private timerID: number | null = null;
  
  private swingAmount: number = 0.0; // 0.0 to 1.0 (delayed even steps)

  constructor() {}

  public init(context: AudioContext): SeqResult<boolean> {
    this.ctx = context;
    return SeqResult.ok(true);
  }

  public setTempo(bpm: number) {
    this.bpm = Math.max(20, Math.min(300, bpm));
  }

  public setSwing(amount: number) {
    this.swingAmount = Math.max(0.0, Math.min(1.0, amount));
  }

  public addTrack(id: string, name: string, steps: number = 16): InstrumentTrack {
    const track: InstrumentTrack = {
      id,
      name,
      buffer: null,
      pattern: Array(steps).fill({ velocity: 0.0 })
    };
    this.tracks.set(id, track);
    return track;
  }

  public setPatternStep(id: string, stepIndex: number, velocity: number): SeqResult<boolean> {
    const track = this.tracks.get(id);
    if (!track) return SeqResult.err({ code: "TRACK_NOT_FOUND", message: `Track ${id} invalid` });
    if (stepIndex < 0 || stepIndex >= track.pattern.length) {
       return SeqResult.err({ code: "INDEX_OOB", message: "Step index out of bounds" });
    }
    track.pattern[stepIndex] = { velocity: Math.max(0, Math.min(1.0, velocity)) };
    return SeqResult.ok(true);
  }

  private nextNote() {
    // Math for 16th notes
    const secondsPerBeat = 60.0 / this.bpm;
    const secondsPer16th = 0.25 * secondsPerBeat;
    
    // Apply swing dynamically to even steps (e.g. 1, 3, 5 based on 0-index)
    let swingOffset = 0;
    if (this.currentStep % 2 !== 0) {
        swingOffset = this.swingAmount * secondsPer16th * 0.5; 
    }

    this.nextNoteTime += secondsPer16th + swingOffset;
    this.currentStep++;
    
    // assuming standard 16 step grid looping
    if (this.currentStep === 16) {
        this.currentStep = 0;
    }
  }

  private scheduleNote(stepNumber: number, time: number) {
    if (!this.ctx) return;

    for (const track of this.tracks.values()) {
        const hit = track.pattern[stepNumber];
        if (hit.velocity > 0.0 && track.buffer) {
            const source = this.ctx.createBufferSource();
            const gain = this.ctx.createGain();
            
            source.buffer = track.buffer;
            gain.gain.value = hit.velocity;

            source.connect(gain);
            gain.connect(this.ctx.destination);
            
            source.start(time);
        }
    }
  }

  private scheduler = () => {
    if (!this.ctx) return;
    
    // Pre-calculate notes that will fall into the scheduling buffer slice
    while (this.nextNoteTime < this.ctx.currentTime + this.scheduleAheadTime) {
        this.scheduleNote(this.currentStep, this.nextNoteTime);
        this.nextNote();
    }
    this.timerID = requestAnimationFrame(this.scheduler);
  }

  public play(): SeqResult<boolean> {
    if (!this.ctx) return SeqResult.err({ code: "NO_CTX", message: "Initialize first" });
    if (this.isPlaying) return SeqResult.ok(true);

    if (this.ctx.state === 'suspended') this.ctx.resume();

    this.isPlaying = true;
    this.currentStep = 0;
    this.nextNoteTime = this.ctx.currentTime + 0.1;

    this.scheduler();
    return SeqResult.ok(true);
  }

  public stop(): SeqResult<boolean> {
    this.isPlaying = false;
    if (this.timerID !== null) cancelAnimationFrame(this.timerID);
    return SeqResult.ok(true);
  }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "SeqResult",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
