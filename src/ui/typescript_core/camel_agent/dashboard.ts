// OMNI Interface Layer - Multi-Agent Dashboard Metrics
export interface AgentMetrics {
    agentId: string;
    cpuUsage: number;
    memoryUsage: number;
    activeTasks: number;
}

export class AgentDashboardManager {
    private agents: Map<string, AgentMetrics> = new Map();

    public updateMetrics(metrics: AgentMetrics): void {
        if (!metrics.agentId) throw new Error("Invalid agent ID");
        this.agents.set(metrics.agentId, metrics);
    }

    public getSystemHealth(): number {
        if (this.agents.size === 0) return 0;
        let totalHealth = 0;
        for (const metric of this.agents.values()) {
            const load = (metric.cpuUsage + metric.memoryUsage) / 2;
            totalHealth += (100 - load);
        }
        return totalHealth / this.agents.size;
    }
}
