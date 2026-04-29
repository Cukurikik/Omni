export interface AriaPayload {
    command: string;
    strictMode: boolean;
}

export class OmniAriaAPI {
    /** OMNI Interface Layer: Aria API */
    public static routeCommand(payload: AriaPayload): string {
        return payload.strictMode ? `STRICT: ${payload.command}` : `RAW: ${payload.command}`;
    }
}
