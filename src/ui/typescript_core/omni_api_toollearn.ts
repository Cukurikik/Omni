export interface ToolExecution {
    toolName: string;
    status: string;
}

export class OmniToolLearnAPI {
    /** OMNI Interface Layer: ToolLearning API */
    public static reportExecution(exec: ToolExecution): string {
        return `Tool [${exec.toolName}] executed with status: ${exec.status}`;
    }
}
