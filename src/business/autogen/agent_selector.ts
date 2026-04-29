// OMNI AUTOGEN: Agent Selector
// TypeScript domain logic for dynamically determining which agent should speak next
// in a multi-agent conversational framework.
// Source: microsoft/autogen

export type AutoGenAgent = {
    name: string;
    description: string;
    systemMessage: string;
};

export class AgentSelector {
    private agents: Map<string, AutoGenAgent> = new Map();

    public registerAgent(agent: AutoGenAgent) {
        this.agents.set(agent.name, agent);
    }

    /**
     * Determines the next speaker based on conversation history and transitions.
     * In a full implementation, this uses an LLM call to evaluate who should speak.
     * Here, we use deterministic heuristics for the structural engine.
     */
    public selectNextSpeaker(
        lastSpeakerName: string, 
        lastMessageContent: string
    ): AutoGenAgent | null {
        if (this.agents.size === 0) return null;

        // Rule 1: If code was just generated, send to Executor/Reviewer
        if (lastMessageContent.includes('```python') || lastMessageContent.includes('```bash')) {
            return this.agents.get('CodeExecutor') || this.agents.get('Reviewer') || null;
        }

        // Rule 2: If execution failed, send back to Coder
        if (lastMessageContent.includes('Error:') || lastMessageContent.includes('Exception:')) {
            return this.agents.get('Coder') || null;
        }

        // Rule 3: If task says TERMINATE, stop
        if (lastMessageContent.includes('TERMINATE')) {
            return null;
        }

        // Default Round-Robin fallback (mocking LLM dynamic selection)
        const agentNames = Array.from(this.agents.keys());
        const currentIndex = agentNames.indexOf(lastSpeakerName);
        
        if (currentIndex === -1 || currentIndex === agentNames.length - 1) {
            return this.agents.get(agentNames[0]) || null;
        }

        return this.agents.get(agentNames[currentIndex + 1]) || null;
    }
}
