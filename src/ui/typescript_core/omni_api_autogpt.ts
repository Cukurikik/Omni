export interface AgentTask {
    id: string;
    description: string;
    isCompleted: boolean;
}

export class OmniAutoGPTAPI {
    /** OMNI Interface Layer: AutoGPT API */
    public static getNextTask(tasks: AgentTask[]): AgentTask | null {
        return tasks.find(t => !t.isCompleted) || null;
    }

    public static completeTask(task: AgentTask): AgentTask {
        return { ...task, isCompleted: true };
    }
}
