export interface AgentMetrics {
    agentId: string;
    calls: number;
}

export class OmniAgentWatchAPI {
    /** OMNI Interface Layer: AgentWatch API */
    public static dashboardUpdate(metrics: AgentMetrics): string {
        return `Dashboard | Agent ${metrics.agentId} | Calls: ${metrics.calls}`;
    }
}
