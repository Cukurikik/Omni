/**
 * OMNI Gemini Vision UI Engine — Interface Layer
 * Absorbing iamsrikanthnani/gemini: Camera + speech recognition vision assistant.
 * TypeScript state management for multimodal input capture.
 */

export interface GeminiUiResult<T> {
    ok: boolean;
    data?: T;
    error?: string;
}

interface CapturedFrame {
    timestamp: number;
    width: number;
    height: number;
    dataUri: string;
}

export class OmniGeminiVisionUiEngine {
    private capturedFrames: CapturedFrame[] = [];
    private isListening: boolean = false;
    private interactions: number = 0;

    public captureFrame(width: number, height: number, dataUri: string): GeminiUiResult<string> {
        if (width <= 0 || height <= 0) {
            return { ok: false, error: 'GeminiUiError: Invalid frame dimensions' };
        }
        if (!dataUri || dataUri.length === 0) {
            return { ok: false, error: 'GeminiUiError: Empty data URI' };
        }
        this.interactions++;
        const frame: CapturedFrame = { timestamp: Date.now(), width, height, dataUri };
        this.capturedFrames.push(frame);
        // Keep only last 30 frames to prevent memory bloat
        if (this.capturedFrames.length > 30) {
            this.capturedFrames = this.capturedFrames.slice(-30);
        }
        return { ok: true, data: `frame-${this.capturedFrames.length}` };
    }

    public toggleVoiceListening(): GeminiUiResult<boolean> {
        this.isListening = !this.isListening;
        this.interactions++;
        return { ok: true, data: this.isListening };
    }

    public getLatestFrame(): GeminiUiResult<CapturedFrame> {
        if (this.capturedFrames.length === 0) {
            return { ok: false, error: 'GeminiUiError: No frames captured' };
        }
        return { ok: true, data: this.capturedFrames[this.capturedFrames.length - 1] };
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: 'OmniGeminiVisionUiEngine',
            frames: this.capturedFrames.length,
            listening: this.isListening,
            interactions: this.interactions,
            status: 'Operational'
        };
    }
}
