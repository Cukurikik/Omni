export interface AgentState {
    id: string;
    role: string;
    status: 'idle' | 'working' | 'error';
}

export function updateAgentState(state: AgentState): void {
    const element = document.getElementById(`agent-${state.id}`);
    if (element) {
        element.className = `agent-node status-${state.status}`;
        element.setAttribute("data-role", state.role);
    }
}
