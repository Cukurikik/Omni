/**
 * OMNI Voice SDK Ionic — Interface Layer
 * Absorbing alan-ai/alan-sdk-ionic: Voice AI integration for Ionic/Angular/React apps.
 * TypeScript voice button state machine and visual feedback controller.
 */

export type VoiceButtonState = 'idle' | 'listening' | 'processing' | 'speaking' | 'error';

export interface VoiceIonicResult<T> {
    ok: boolean;
    data?: T;
    error?: string;
}

export class OmniVoiceSdkIonicEngine {
    private state: VoiceButtonState = 'idle';
    private transitions: number = 0;
    private handlers: Map<string, (payload: any) => any> = new Map();

    private readonly validTransitions: Record<VoiceButtonState, VoiceButtonState[]> = {
        idle: ['listening'],
        listening: ['processing', 'idle', 'error'],
        processing: ['speaking', 'idle', 'error'],
        speaking: ['idle'],
        error: ['idle']
    };

    public transition(to: VoiceButtonState): VoiceIonicResult<VoiceButtonState> {
        if (!this.validTransitions[this.state]?.includes(to)) {
            return { ok: false, error: `VoiceIonicError: Invalid transition ${this.state} → ${to}` };
        }
        this.state = to;
        this.transitions++;
        return { ok: true, data: this.state };
    }

    public registerCommand(command: string, handler: (payload: any) => any): VoiceIonicResult<boolean> {
        if (!command) return { ok: false, error: 'VoiceIonicError: Empty command' };
        this.handlers.set(command, handler);
        return { ok: true, data: true };
    }

    public executeCommand(command: string, payload: any = {}): VoiceIonicResult<any> {
        if (!this.handlers.has(command)) {
            return { ok: false, error: `VoiceIonicError: Unknown command '${command}'` };
        }
        try {
            const result = this.handlers.get(command)!(payload);
            return { ok: true, data: result };
        } catch (e: any) {
            return { ok: false, error: `VoiceIonicError: ${e.message}` };
        }
    }

    public getState(): VoiceButtonState { return this.state; }

    public diagnostics(): Record<string, any> {
        return {
            engine: 'OmniVoiceSdkIonicEngine',
            state: this.state,
            transitions: this.transitions,
            commands: this.handlers.size,
            status: 'Operational'
        };
    }
}
