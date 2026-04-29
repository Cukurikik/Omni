/// <reference lib="dom" />
/// <reference types="node" />
/**
 * OmniWebAudioSpatialEngine — Production-Grade Web UI Spatialization
 * ===================================================================
 * Absorbed from: mdn/webaudio-examples
 *
 * Key patterns learned and implemented:
 * - 3D PannerNode configurations (HRTF context)
 * - Distance models (inverse, linear, exponential)
 * - Pure UI AudioContext tracking ensuring no memory locks
 *
 * OMNI Layer: ui/typescript_core
 * @since 2026.4.0
 * @tags ["audio", "webaudio", "spatial", "3d", "mdn"]
 */

export interface SpatialError {
    code: string;
    message: string;
}

export class SpatialResult<T> {
    private constructor(
        private readonly _value: T | null,
        private readonly _error: SpatialError | null,
        private readonly _isOk: boolean
    ) {}

    public static ok<T>(value: T): SpatialResult<T> { return new SpatialResult<T>(value, null, true); }
    public static err<T>(error: SpatialError): SpatialResult<T> { return new SpatialResult<T>(null, error, false); }
    
    public get isOk(): boolean { return this._isOk; }
    
    public unwrap(): T {
        if (!this._isOk || this._error) throw new Error(this._error?.message);
        return this._value as T;
    }
}

export interface Vec3 {
    x: number;
    y: number;
    z: number;
}

export class OmniWebAudioSpatialEngine {
    private ctx: AudioContext | null = null;
    private listener: AudioListener | null = null;
    
    // Map to hold Panner nodes decoupling them from memory garbage collectors dynamically
    private panners: Map<string, PannerNode> = new Map();

    constructor() {}

    public initContext(context: AudioContext): SpatialResult<boolean> {
        this.ctx = context;
        this.listener = context.listener;

        // Default strict listener orientation mapped directly from MDN Physics standard setup
        if (this.listener) {
             // Forward orientation Vector
            this.setListenerOrientation({ x: 0, y: 0, z: -1 }, { x: 0, y: 1, z: 0 });
            this.setListenerPosition({ x: 0, y: 0, z: 0 });
        }
        return SpatialResult.ok(true);
    }

    public setListenerPosition(pos: Vec3) {
        if (!this.listener) return;
        // Handling MDN deprecations cleanly backwards compatible with legacy setPosition
        if (this.listener.positionX) {
            this.listener.positionX.value = pos.x;
            this.listener.positionY.value = pos.y;
            this.listener.positionZ.value = pos.z;
        } else {
            (this.listener as any).setPosition(pos.x, pos.y, pos.z);
        }
    }

    public setListenerOrientation(forward: Vec3, up: Vec3) {
         if (!this.listener) return;
         if (this.listener.forwardX) {
            this.listener.forwardX.value = forward.x;
            this.listener.forwardY.value = forward.y;
            this.listener.forwardZ.value = forward.z;
            this.listener.upX.value = up.x;
            this.listener.upY.value = up.y;
            this.listener.upZ.value = up.z;
         } else {
             (this.listener as any).setOrientation(forward.x, forward.y, forward.z, up.x, up.y, up.z);
         }
    }

    public create3DSource(id: string, distanceModel: DistanceModelType = 'inverse'): SpatialResult<PannerNode> {
        if (!this.ctx) return SpatialResult.err({ code: "NO_CTX", message: "Call initContext first" });

        const panner = this.ctx.createPanner();
        panner.panningModel = 'HRTF';
        panner.distanceModel = distanceModel;
        panner.refDistance = 1;
        panner.maxDistance = 10000;
        panner.rolloffFactor = 1;
        panner.coneInnerAngle = 360;
        panner.coneOuterAngle = 0;
        panner.coneOuterGain = 0;

        this.panners.set(id, panner);
        return SpatialResult.ok(panner);
    }

    public updateSourcePosition(id: string, pos: Vec3): SpatialResult<boolean> {
        const panner = this.panners.get(id);
        if (!panner) return SpatialResult.err({ code: "NOT_FOUND", message: `Panner ${id} unallocated` });

        if (panner.positionX) {
            panner.positionX.value = pos.x;
            panner.positionY.value = pos.y;
            panner.positionZ.value = pos.z;
        } else {
            (panner as any).setPosition(pos.x, pos.y, pos.z);
        }
        return SpatialResult.ok(true);
    }

    public connectSource(id: string, source: AudioNode): SpatialResult<boolean> {
        const panner = this.panners.get(id);
        if (!panner) return SpatialResult.err({ code: "NOT_FOUND", message: `Panner ${id} unallocated` });
        
        if (!this.ctx) return SpatialResult.err({ code: "NO_CTX", message: "Ctx Missing" });

        source.connect(panner);
        panner.connect(this.ctx.destination);
        
        return SpatialResult.ok(true);
    }

    public removeSource(id: string): void {
        const panner = this.panners.get(id);
        if (panner) {
            panner.disconnect();
            this.panners.delete(id);
        }
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "SpatialResult",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
