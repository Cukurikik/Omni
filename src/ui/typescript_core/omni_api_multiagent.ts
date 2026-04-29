export interface AgentMessage {
    agentId: string;
    thought: string;
}

export class OmniMultiAgentAPI {
    /** OMNI Interface Layer: Multi-Agent API */
    public static compileDebate(messages: AgentMessage[]): string {
        return messages.map(m => `Agent[${m.agentId}]: ${m.thought}`).join('\n---\n');
    }

    public static checkDeadlock(messages: AgentMessage[]): boolean {
        // Simple deadlock heuristics: same thought repeated
        if (messages.length < 4) return false;
        return messages[messages.length - 1].thought === messages[messages.length - 3].thought;
    }
}
