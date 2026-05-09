//=============================================================================
// OMNI INTERFACE LAYER — AGENT TASK LOG (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: UI component for viewing detailed task execution logs of Swarm Agents.
//=============================================================================

import React, { useState, useEffect } from 'react';
import { NetworkClient } from '@omni-bridge/network';

interface TaskLogEntry {
    id: string;
    agentId: string;
    description: string;
    status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED';
    result?: string;
    timestamp: string;
}

/**
 * @html_template("agent-task-log")
 */
export const AgentTaskLog: React.FC<{ agentId: string }> = ({ agentId }) => {
    const [logs, setLogs] = useState<TaskLogEntry[]>([]);

    useEffect(() => {
        // Subscribe to real-time agent log events
        const sub = NetworkClient.subscribeToEvent(`agent.${agentId}.logs`, (entry: TaskLogEntry) => {
            setLogs(prev => [entry, ...prev].slice(0, 50)); // Keep last 50
        });

        return () => sub.unsubscribe();
    }, [agentId]);

    return (
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 h-96 flex flex-col">
            <h3 className="text-lg font-bold text-cyan-400 mb-4 border-b border-gray-700 pb-2">
                Execution Log: {agentId}
            </h3>
            
            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                {logs.length === 0 ? (
                    <p className="text-gray-500 text-sm italic text-center mt-10">No recent activity.</p>
                ) : (
                    logs.map(log => (
                        <div key={log.id} className="bg-gray-900 p-3 rounded text-sm border-l-2 border-cyan-500">
                            <div className="flex justify-between items-center mb-1">
                                <span className="font-mono text-gray-400 text-xs">{new Date(log.timestamp).toLocaleTimeString()}</span>
                                <span className={`text-xs font-bold ${
                                    log.status === 'COMPLETED' ? 'text-green-400' :
                                    log.status === 'FAILED' ? 'text-red-400' : 'text-yellow-400'
                                }`}>{log.status}</span>
                            </div>
                            <p className="text-gray-300">{log.description}</p>
                            {log.result && (
                                <p className="mt-2 text-xs text-gray-400 font-mono bg-black p-2 rounded">
                                    > {log.result}
                                </p>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};
