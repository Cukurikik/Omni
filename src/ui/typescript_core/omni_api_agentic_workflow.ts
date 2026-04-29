export interface WorkflowStep {
    stepId: string;
    dependencies: string[];
    status: 'pending' | 'running' | 'done';
}

export class OmniAgenticWorkflowAPI {
    /** OMNI Interface: Agentic Workflow API */
    public static isReady(step: WorkflowStep, completedIds: Set<string>): boolean {
        return step.dependencies.every(d => completedIds.has(d));
    }
}
