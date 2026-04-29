import React from 'react';

interface AgentState {
    id: string;
    role: string;
    activeTask: string | null;
}

export const SwarmsMonitor = ({ agents }: { agents: AgentState[] }) => {
    return (
        <div className="swarms-monitor">
            <h2>Swarms Active Agents</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
                {agents.map(a => (
                    <div key={a.id} style={{ border: '1px solid #444', padding: '10px' }}>
                        <h3>{a.id} ({a.role})</h3>
                        <p>Task: {a.activeTask || 'Idle'}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};
