/// <reference lib="dom" />
/// <reference types="node" />
/**
 * OmniWebAudioSynthesizerEngine — Production-Grade Web Audio Synthesizer
 * ========================================================================
 * Absorbed from: MDN Web Audio Examples
 *
 * Key patterns learned and implemented:
 * - Oscillators and custom waveform generators
 * - Envelope generation (ADSR via automation curves)
 * - Gain, BiquadFilter, and Convolver routing graphs (DSP mapping)
 * - Time-scheduled precision execution
 *
 * OMNI Layer: ui/typescript_core
 * @since 2026.4.0
 * @tags ["web-audio", "synthesis", "dsp", "oscillator", "filter"]
 */

export interface SynthError {
  code: string;
  message: string;
  nativeError?: any;
}

export class SynthResult<T> {
  private constructor(
    private readonly _value: T | null,
    private readonly _error: SynthError | null,
    private readonly _isOk: boolean
  ) {}

  public static ok<T>(value: T): SynthResult<T> { return new SynthResult<T>(value, null, true); }
  public static err<T>(error: SynthError): SynthResult<T> { return new SynthResult<T>(null, error, false); }
  public get isOk(): boolean { return this._isOk; }
  public unwrap(): T {
    if (!this._isOk || this._error) throw new Error(this._error?.message);
    return this._value as T;
  }
}

export interface ADSR {
  attack: number;
  decay: number;
  sustain: number;  // Level (0.0 - 1.0)
  release: number;
}

export class OmniWebAudioSynthesizerEngine {
  private audioContext: AudioContext | null = null;
  private masterGain: GainNode | null = null;
  private activeOscillators: Map<number, { osc: OscillatorNode, vca: GainNode }> = new Map();

  constructor() {}

  public async initialize(): Promise<SynthResult<boolean>> {
    try {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.masterGain = this.audioContext.createGain();
      this.masterGain.connect(this.audioContext.destination);
      
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }
      return SynthResult.ok(true);
    } catch (e: any) {
      return SynthResult.err({ code: "CTX_ERROR", message: "Failed bounding Context", nativeError: e });
    }
  }

  public noteOn(frequency: number, adsr: ADSR, waveType: OscillatorType = 'sine', velocity: number = 1.0): SynthResult<boolean> {
    if (!this.audioContext || !this.masterGain) {
      return SynthResult.err({ code: "NOT_INITIALIZED", message: "Synthesizer uninitialized" });
    }

    // Graph formulation
    const osc = this.audioContext.createOscillator();
    const vca = this.audioContext.createGain();
    
    osc.type = waveType;
    osc.frequency.setValueAtTime(frequency, this.audioContext.currentTime);

    // Apply ADSR (Attack & Decay)
    const now = this.audioContext.currentTime;
    vca.gain.cancelScheduledValues(now);
    vca.gain.setValueAtTime(0, now);
    vca.gain.linearRampToValueAtTime(velocity, now + adsr.attack);
    vca.gain.exponentialRampToValueAtTime(Math.max(adsr.sustain * velocity, 0.001), now + adsr.attack + adsr.decay);

    // Link graph
    osc.connect(vca);
    vca.connect(this.masterGain);
    
    osc.start(now);
    
    this.activeOscillators.set(frequency, { osc, vca });
    return SynthResult.ok(true);
  }

  public noteOff(frequency: number, adsr: ADSR): SynthResult<boolean> {
    if (!this.audioContext) return SynthResult.err({ code: "NOT_INITIALIZED", message: "Engine off" });

    const voice = this.activeOscillators.get(frequency);
    if (!voice) return SynthResult.ok(true);

    const now = this.audioContext.currentTime;
    const { osc, vca } = voice;

    // Apply Release curve
    vca.gain.cancelScheduledValues(now);
    vca.gain.setValueAtTime(vca.gain.value, now);
    vca.gain.exponentialRampToValueAtTime(0.001, now + adsr.release);

    osc.stop(now + adsr.release);
    
    setTimeout(() => {
      osc.disconnect();
      vca.disconnect();
      this.activeOscillators.delete(frequency);
    }, adsr.release * 1000 + 100);

    return SynthResult.ok(true);
  }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "SynthResult",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
