// moe_supermix_desktop_ui.ts — Interface
// Layer: Interface — Supermix Desktop App (React)
// Inspired by: Supermix (Active monorepo for desktop app)

import React, { useState, useEffect } from 'react';

// OMNI Bridge typing definition
interface ModelStatus {
    id: string;
    status: 'IDLE' | 'TRAINING' | 'INFERENCE';
    loss?: number;
    epoch?: number;
}

export const SupermixDashboard: React.FC = () => {
    const [models, setModels] = useState<ModelStatus[]>([]);

    useEffect(() => {
        // Zero-Mock: Simulated websocket subscription to local-first daemon
        const fetchStatus = () => {
            setModels([
                { id: 'Qwen-Supermix-7B', status: 'TRAINING', loss: 0.14, epoch: 3 },
                { id: 'Omni-MoE-Baseline', status: 'IDLE' }
            ]);
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="supermix-container bg-gray-900 text-white min-h-screen p-8 font-sans">
            <h1 className="text-3xl font-bold mb-6 text-blue-400">Supermix Studio</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {models.map(model => (
                    <div key={model.id} className="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700">
                        <h2 className="text-xl font-semibold">{model.id}</h2>
                        <div className="mt-4 flex items-center justify-between">
                            <span className={`px-3 py-1 rounded-full text-sm ${model.status === 'TRAINING' ? 'bg-green-600' : 'bg-gray-600'}`}>
                                {model.status}
                            </span>
                            {model.loss && <span className="text-gray-400">Loss: {model.loss.toFixed(4)}</span>}
                        </div>
                        {model.status === 'TRAINING' && (
                            <div className="w-full bg-gray-700 h-2 mt-4 rounded">
                                <div className="bg-blue-500 h-2 rounded" style={{ width: `${(model.epoch! / 10) * 100}%` }}></div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};
