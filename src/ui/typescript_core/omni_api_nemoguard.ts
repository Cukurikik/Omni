export interface GuardrailEvent {
    requestId: string;
    isBlocked: boolean;
    reason: string;
}

export class OmniNeMoGuardAPI {
    /** OMNI Interface Layer: NeMo-Guardrails API */
    public static emitEvent(event: GuardrailEvent): string {
        return `[GUARDRAIL] Req ${event.requestId}: Blocked=${event.isBlocked} (${event.reason})`;
    }
}
