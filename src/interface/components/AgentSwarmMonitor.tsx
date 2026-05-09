//=============================================================================
// OMNI INTERFACE LAYER — SWARM MONITOR (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: UI for monitoring active agents in the Swarms framework.
//=============================================================================

import React, { useState, useEffect } from 'react';
import { NetworkClient } from '@omni-bridge/network';

interface Agent {
    id: string;
    role: string;
    status: 'IDLE' | 'WORKING' | 'ERROR';
    currentTask?: string;
}

/**
 * @html_template("swarm-monitor")
 */
export const AgentSwarmMonitor: React.FC = () => {
    const [agents, setAgents] = useState<Agent[]>([]);

    useEffect(() => {
        const fetchAgents = async () => {
            const res = await NetworkClient.graphqlQuery<{getActiveAgents: Agent[]}>('query { getActiveAgents { id role status currentTask } }');
            if (res.isOk()) {
                setAgents(res.unwrap().getActiveAgents);
            }
        };

        fetchAgents();
        // Polling loop for active swarm status
        const interval = setInterval(fetchAgents, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 bg-gray-900 rounded-lg shadow-xl text-white h-full overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span className="text-purple-400">⚡</span> Swarm Hive Mind
            </h2>
            
            <div className="grid gap-4">
                {agents.map(agent => (
                    <div key={agent.id} className="bg-gray-800 p-4 rounded-md border border-gray-700 flex justify-between items-center transition-all hover:border-purple-500">
                        <div>
                            <h3 className="font-semibold text-lg text-cyan-300">{agent.role}</h3>
                            <p className="text-xs text-gray-400">ID: {agent.id}</p>
                            {agent.currentTask && (
                                <p className="text-sm text-gray-300 mt-2">
                                    <span className="font-medium text-gray-500">Task:</span> {agent.currentTask}
                                </p>
                            )}
                        </div>
                        <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                            agent.status === 'WORKING' ? 'bg-green-900 text-green-300' :
                            agent.status === 'ERROR' ? 'bg-red-900 text-red-300' :
                            'bg-gray-700 text-gray-300'
                        }`}>
                            {agent.status}
                        </div>
                    </div>
                ))}

                {agents.length === 0 && (
                    <div className="text-center text-gray-500 py-10">
                        No active agents in the Swarm.
                    </div>
                )}
            </div>
        </div>
    );
};
