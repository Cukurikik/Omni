/// <reference lib="dom" />
/// <reference types="node" />
/**
 * omni_dynamic_audio_engine.ts
 * Production-Grade Dynamic Audio PCM Engine
 * ==============================================================
 * Absorbed from: bfirsh/dynamicaudio.js
 *
 * Key patterns learned:
 * - Direct buffering of -1.0 to 1.0 f32 PCM samples into Web Audio API.
 * - Buffer underrun management.
 *
 * OMNI Layer: ui/ts_core (Interface Bridge)
 * @since 2026.4.0
 */

export class DynamicAudioEngineError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'DynamicAudioEngineError';
    }
}

export interface DynamicAudioOptions {
    sampleRate?: number;
    bufferSize?: number;
    channels?: number;
}

export class OmniDynamicAudioEngine {
    private context: AudioContext | null = null;
    private scriptNode: ScriptProcessorNode | null = null;
    
    // Internal PCM buffer
    private sampleRate: number;
    private bufferSize: number;
    private channels: number;
    private sampleBuffer: Float32Array;
    private writePos: number = 0;
    private readPos: number = 0;
    
    private isPlaying: boolean = false;

    constructor(options: DynamicAudioOptions = {}) {
        this.sampleRate = options.sampleRate || 44100;
        this.bufferSize = options.bufferSize || 4096;
        this.channels = options.channels || 2;
        
        // Ring buffer to hold queued samples (large enough to prevent underruns)
        this.sampleBuffer = new Float32Array(this.sampleRate * this.channels * 2);
    }

    /**
     * Initializes the Web Audio Context (must be called after a user interaction 
     * due to browser autoplay policies)
     */
    public initialize(): void {
        if (this.context) return;
        
        try {
            const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
            this.context = new AudioContextClass({ sampleRate: this.sampleRate });
            
            // Note: ScriptProcessorNode is formally deprecated but broadly supported.
            // In a production WebAssembly paradigm, an AudioWorklet is preferred,
            // but this replicates dynamicaudio.js's synchronous JS callback pattern safely.
            this.scriptNode = this.context.createScriptProcessor(this.bufferSize, 0, this.channels);
            this.scriptNode.onaudioprocess = (e: AudioProcessingEvent) => this.onAudioProcess(e);
            
            this.scriptNode.connect(this.context.destination);
            this.isPlaying = true;
        } catch (e) {
            throw new DynamicAudioEngineError(`Failed to initialize AudioContext: ${(e as Error).message}`);
        }
    }

    /**
     * Writes raw Float32 samples (-1.0 to 1.0) into the ring buffer.
     * @param samples Array of f32 samples
     */
    public write(samples: Float32Array | number[]): void {
        if (!this.isPlaying) {
            this.initialize();
        }

        const len = samples.length;
        const capacity = this.sampleBuffer.length;
        
        for (let i = 0; i < len; i++) {
            this.sampleBuffer[this.writePos] = samples[i];
            this.writePos = (this.writePos + 1) % capacity;
            
            if (this.writePos === this.readPos) {
                // Buffer overflow: force read pointer forward (dropping oldest)
                this.readPos = (this.readPos + 1) % capacity; 
            }
        }
    }

    /**
     * Helper to write 16-bit integer PCM sequences.
     */
    public writeInt16(samples: Int16Array | number[]): void {
        const floatSamples = new Float32Array(samples.length);
        for (let i = 0; i < samples.length; i++) {
            floatSamples[i] = samples[i] / 32768.0;
        }
        this.write(floatSamples);
    }

    /**
     * Standard Web Audio Callback draining the ring buffer
     */
    private onAudioProcess(event: AudioProcessingEvent): void {
        const outputBuffer = event.outputBuffer;
        
        for (let channel = 0; channel < this.channels; channel++) {
            const channelData = outputBuffer.getChannelData(channel);
            
            for (let i = 0; i < outputBuffer.length; i++) {
                // De-interleave from ring buffer if we have data
                if (this.readPos !== this.writePos) {
                    channelData[i] = this.sampleBuffer[this.readPos];
                    this.readPos = (this.readPos + 1) % this.sampleBuffer.length;
                } else {
                    // Buffer underrun
                    channelData[i] = 0.0;
                }
            }
        }
    }

    public stop(): void {
        if (this.scriptNode && this.context) {
            this.scriptNode.disconnect();
            this.context.close();
        }
        this.isPlaying = false;
        this.context = null;
        this.scriptNode = null;
        this.writePos = 0;
        this.readPos = 0;
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "DynamicAudioEngineError",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
