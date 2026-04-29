export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class AgentMonitorUI {
    public updateToolUsage(agentId: string, toolLogs: string[]): OmniResult<boolean> {
        if (!agentId || toolLogs.length === 0) {
            return { value: false, error: "Invalid agent or logs", isOk: false };
        }

        // Native DOM update for RL tool orchestration dashboard
        console.log(`Agent ${agentId} orchestrated tools: ${toolLogs.join(", ")}`);
        
        return { value: true, error: null, isOk: true };
    }
}
