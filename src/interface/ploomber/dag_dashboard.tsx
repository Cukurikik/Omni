import React, { useState, useEffect } from 'react';

// OMNI Ploomber - DAG Execution Dashboard
// Real-time React dashboard for observing pipeline status

interface TaskStatus {
    id: string;
    name: string;
    status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';
    duration?: number;
}

export const DAGDashboard: React.FC = () => {
    const [tasks, setTasks] = useState<TaskStatus[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // In a real implementation, this connects to the OMNI Event Bus (Kafka)
        // Here we simulate the initial fetch structure for type adherence
        const fetchTasks = async () => {
            try {
                // Mock payload to demonstrate UI rendering without breaking strict types
                setTasks([
                    { id: '1', name: 'extract_data', status: 'COMPLETED', duration: 45 },
                    { id: '2', name: 'transform_data', status: 'RUNNING' },
                    { id: '3', name: 'load_data', status: 'PENDING' }
                ]);
            } catch (err: any) {
                setError(err.message);
            }
        };

        fetchTasks();
    }, []);

    if (error) {
        return <div className="text-red-500 bg-red-100 p-4 rounded border border-red-400">Error: {error}</div>;
    }

    return (
        <div className="p-6 bg-slate-900 min-h-screen text-slate-200">
            <h1 className="text-3xl font-bold text-blue-400 mb-6">Ploomber DAG Execution Monitor</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks.map(task => (
                    <div key={task.id} className="bg-slate-800 p-4 rounded-lg shadow border border-slate-700">
                        <h3 className="text-xl font-semibold">{task.name}</h3>
                        <div className="mt-2 flex items-center">
                            <span className="text-gray-400 mr-2">Status:</span>
                            <span className={`font-mono px-2 py-1 rounded text-sm ${
                                task.status === 'COMPLETED' ? 'bg-green-900 text-green-300' :
                                task.status === 'RUNNING' ? 'bg-blue-900 text-blue-300' :
                                task.status === 'FAILED' ? 'bg-red-900 text-red-300' :
                                'bg-gray-700 text-gray-300'
                            }`}>
                                {task.status}
                            </span>
                        </div>
                        {task.duration && (
                            <div className="mt-2 text-sm text-gray-500">
                                Duration: {task.duration}s
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
