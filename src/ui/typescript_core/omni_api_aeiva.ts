export interface AgentState {
    stateId: string;
    value: number;
    reward: number;
}

export class OmniAeivaAPI {
    /** OMNI Interface: AEIVA Agent API */
    public static bellmanUpdate(s: AgentState, nextValue: number, gamma: number, alpha: number): number {
        const target = s.reward + gamma * nextValue;
        return s.value + alpha * (target - s.value);
    }
}
