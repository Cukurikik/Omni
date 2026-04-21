/// <reference lib="dom" />
/// <reference types="node" />
// omni_webaudio_examples_engine.ts
// Production-Grade Web Audio API Examples & Utilities Engine
// ==============================================================
// Absorbed from: mdn/webaudio-examples
//
// OMNI Layer: ui/typescript_core
// @since 2026.4.0

const ENGINE_VERSION = "1.0.0-omni";

interface OscillatorConfig { type: "sine" | "square" | "sawtooth" | "triangle"; frequency: number; detune: number; }
interface FilterConfig { type: "lowpass" | "highpass" | "bandpass" | "notch" | "peaking"; frequency: number; Q: number; gain: number; }
interface ConvolverConfig { impulseLength: number; decay: number; reverse: boolean; }
interface AnalyserConfig { fftSize: number; smoothing: number; minDb: number; maxDb: number; }

class WebAudioExamplesError extends Error {
    constructor(public code: string, msg: string) { super(msg); this.name = "WebAudioExamplesError"; }
}

/**
 * Production-grade Web Audio API utilities engine.
 *
 * Provides node graph construction, oscillator management,
 * filter design, convolution reverb, analyser visualization,
 * and audio worklet scaffolding.
 */
export class OmniWebaudioExamplesEngine {
    private nodes: Map<string, { type: string; config: Record<string, unknown> }> = new Map();
    private connections: Array<{ from: string; to: string }> = [];
    private sampleRate: number;

    constructor(sampleRate: number = 44100) {
        this.sampleRate = sampleRate;
    }

    /** Create an oscillator node configuration. */
    createOscillator(id: string, config: OscillatorConfig): {
        status: string; data: { id: string; config: OscillatorConfig; nyquist: number };
    } {
        if (config.frequency <= 0 || config.frequency > this.sampleRate / 2) {
            throw new WebAudioExamplesError("FREQ_RANGE", `Frequency out of range (0, ${this.sampleRate / 2}]`);
        }
        this.nodes.set(id, { type: "oscillator", config: config as any });
        return { status: "success", data: { id, config, nyquist: this.sampleRate / 2 } };
    }

    /** Create a biquad filter node. */
    createFilter(id: string, config: FilterConfig): {
        status: string; data: { id: string; config: FilterConfig; normalizedFreq: number };
    } {
        const normalizedFreq = config.frequency / (this.sampleRate / 2);
        this.nodes.set(id, { type: "filter", config: config as any });
        return { status: "success", data: { id, config, normalizedFreq: Math.round(normalizedFreq * 10000) / 10000 } };
    }

    /** Design an impulse response for convolution reverb. */
    createConvolverImpulse(config: ConvolverConfig): {
        status: string; data: { samples: number[]; length: number; decay: number };
    } {
        const length = config.impulseLength;
        const samples: number[] = new Array(length);
        for (let i = 0; i < length; i++) {
            const t = config.reverse ? (length - 1 - i) / length : i / length;
            const noise = Math.random() * 2 - 1;
            const envelope = Math.exp(-t * config.decay);
            samples[i] = Math.round(noise * envelope * 1000000) / 1000000;
        }
        return { status: "success", data: { samples, length, decay: config.decay } };
    }

    /** Configure an analyser for frequency/time domain visualization. */
    createAnalyser(id: string, config: AnalyserConfig): {
        status: string; data: {
            id: string; config: AnalyserConfig; frequencyBinCount: number;
            binWidth: number;
        };
    } {
        const validSizes = [32, 64, 128, 256, 512, 1024, 2048, 4096, 8192];
        if (!validSizes.includes(config.fftSize)) {
            throw new WebAudioExamplesError("INVALID_FFT", `FFT size must be power of 2 in [32, 8192]`);
        }
        const frequencyBinCount = config.fftSize / 2;
        const binWidth = this.sampleRate / config.fftSize;
        this.nodes.set(id, { type: "analyser", config: config as any });
        return { status: "success", data: { id, config, frequencyBinCount, binWidth: Math.round(binWidth * 100) / 100 } };
    }

    /** Connect two nodes in the audio graph. */
    connect(fromId: string, toId: string): {
        status: string; data: { from: string; to: string; totalConnections: number };
    } {
        if (!this.nodes.has(fromId)) throw new WebAudioExamplesError("NOT_FOUND", `Node '${fromId}' not found`);
        if (!this.nodes.has(toId)) throw new WebAudioExamplesError("NOT_FOUND", `Node '${toId}' not found`);
        this.connections.push({ from: fromId, to: toId });
        return { status: "success", data: { from: fromId, to: toId, totalConnections: this.connections.length } };
    }

    /** Generate AudioWorklet processor skeleton code. */
    generateWorkletCode(processorName: string, paramNames: string[]): {
        status: string; data: { code: string; processorName: string };
    } {
        const params = paramNames.map(n =>
            `      ['${n}', { defaultValue: 0, minValue: -1, maxValue: 1, automationRate: 'a-rate' }]`
        ).join(",\n");

        const code = `class ${processorName} extends AudioWorkletProcessor {
  static get parameterDescriptors() {
    return [
${params}
    ];
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    const output = outputs[0];
    for (let ch = 0; ch < output.length; ch++) {
      for (let i = 0; i < output[ch].length; i++) {
        output[ch][i] = input[ch] ? input[ch][i] : 0;
      }
    }
    return true;
  }
}
registerProcessor('${processorName}', ${processorName});`;

        return { status: "success", data: { code, processorName } };
    }

    /** Get audio graph summary. */
    getGraphSummary(): {
        status: string; data: {
            totalNodes: number; totalConnections: number;
            nodeTypes: Record<string, number>; sampleRate: number;
        };
    } {
        const nodeTypes: Record<string, number> = {};
        for (const node of this.nodes.values()) {
            nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1;
        }
        return {
            status: "success",
            data: { totalNodes: this.nodes.size, totalConnections: this.connections.length,
                    nodeTypes, sampleRate: this.sampleRate },
        };
    }
}
