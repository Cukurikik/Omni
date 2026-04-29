export interface WorkerStatus {
    workerId: string;
    loadPercentage: number;
}

export class OmniFastChatAPI {
    /** OMNI Interface Layer: FastChat API */
    public static updateRegistry(status: WorkerStatus): string {
        return `Worker ${status.workerId} load updated to ${status.loadPercentage}%`;
    }
}
