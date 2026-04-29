// Omni API for CodeAgents Planner
export interface AgentTaskPlan {
    taskId: string;
    steps: string[];
    estimatedCompletionTimeMs: number;
}

export class OmniCodeAgentsAPI {
    static validatePlanViability(plan: AgentTaskPlan, maxAllowedTimeMs: number): boolean {
        if (!plan.steps || plan.steps.length === 0) return false;
        if (plan.estimatedCompletionTimeMs > maxAllowedTimeMs) return false;
        return true;
    }
}
