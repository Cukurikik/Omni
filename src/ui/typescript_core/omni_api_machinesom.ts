export interface SocietyAgent {
    id: string;
    role: string;
}

export class OmniMachineSoMAPI {
    /** OMNI Interface Layer: MachineSoM API */
    public static initializeAgent(agent: SocietyAgent): string {
        return `[Agent ${agent.id} initialized as ${agent.role}]`;
    }
}
