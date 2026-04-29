export interface MemoryInterrupt {
    reason: string;
    urgency: number;
}

export class OmniMemGPTAPI {
    /** OMNI Interface Layer: MemGPT API */
    public static triggerInterrupt(intr: MemoryInterrupt): string {
        return `[SYSTEM_INTERRUPT Level ${intr.urgency}]: ${intr.reason}. Please yield control to OS.`;
    }
}
