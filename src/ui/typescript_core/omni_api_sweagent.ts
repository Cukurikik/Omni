export interface SWECommand {
    type: 'search' | 'edit' | 'test';
    payload: string;
}

export class OmniSWEAgentAPI {
    /** OMNI Interface Layer: SWE-Agent API */
    public static validateCommand(cmd: SWECommand): boolean {
        if (!cmd.type || !cmd.payload) return false;
        if (cmd.payload.length > 5000) return false; // Prevent overflow
        return true;
    }
}
