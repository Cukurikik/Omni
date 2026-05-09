// OMNI Framework - TypeScript/React Dashboard for AthenaOS Swarm
import React, { useState, useEffect } from 'react';

interface SwarmAgent {
    id: string;
    status: 'IDLE' | 'COMPUTING' | 'ERROR';
    assigned_task: string | null;
}

export const OmniAthenaDashboard: React.FC = () => {
    const [agents, setAgents] = useState<SwarmAgent[]>([]);

    useEffect(() => {
        // Fetch agents from OMNI Rust API Gateway
        setAgents([
            { id: 'agent-alpha', status: 'COMPUTING', assigned_task: 'Optimize Graph' },
            { id: 'agent-beta', status: 'IDLE', assigned_task: null },
            { id: 'agent-gamma', status: 'COMPUTING', assigned_task: 'Train KEMLM' }
        ]);
    }, []);

    return (
        <div className="p-6 bg-gray-900 text-white min-h-screen">
            <h1 className="text-3xl font-bold mb-6 text-blue-400">OMNI AthenaOS Swarm Control</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {agents.map(agent => (
                    <div key={agent.id} className="p-4 border border-gray-700 rounded-lg shadow bg-gray-800">
                        <h2 className="text-xl font-semibold">{agent.id}</h2>
                        <p className={`mt-2 ${agent.status === 'COMPUTING' ? 'text-green-400' : 'text-yellow-400'}`}>
                            Status: {agent.status}
                        </p>
                        {agent.assigned_task && (
                            <p className="mt-1 text-sm text-gray-400">Task: {agent.assigned_task}</p>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
