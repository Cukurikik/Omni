export interface TaskNode {
    taskId: string;
    description: string;
    priority: number;
}

export class OmniAITaskAPI {
    /** OMNI Interface Layer: AI Task API */
    public static formatQueueStatus(queue: TaskNode[]): string {
        return `Queue Length: ${queue.length}\nTop Task: ${queue.length > 0 ? queue[0].taskId : 'None'}`;
    }
}
