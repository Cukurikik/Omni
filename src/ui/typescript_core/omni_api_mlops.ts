export interface PipelineTask {
    id: string;
    priority: number;
    status: 'PENDING' | 'RUNNING' | 'DONE';
}

export class OmniMLOpsAPI {
    /** OMNI Interface Layer: MLOps API */
    public static getPendingTasks(tasks: PipelineTask[]): PipelineTask[] {
        return tasks.filter(t => t.status === 'PENDING');
    }

    public static updateTaskStatus(task: PipelineTask, newStatus: 'RUNNING' | 'DONE'): PipelineTask {
        return { ...task, status: newStatus };
    }
}
