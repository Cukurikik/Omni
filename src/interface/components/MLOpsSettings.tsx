//=============================================================================
// OMNI INTERFACE LAYER — MLOPS SETTINGS (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: UI for managing global MLOps parameters within the Omni Dashboard.
//=============================================================================

import React, { useState } from 'react';
import { NetworkClient } from '@omni-bridge/network';

/**
 * @html_template("mlops-settings")
 */
export const MLOpsSettings: React.FC = () => {
    const [maxSwarmAgents, setMaxSwarmAgents] = useState(10);
    const [useDiffTransformer, setUseDiffTransformer] = useState(true);
    const [gpuMemoryLimit, setGpuMemoryLimit] = useState(8192); // MB

    const handleSave = async () => {
        // Dispatch config updates to Go/Rust system layers
        await NetworkClient.invokeCommand('system.config.update_mlops', {
            max_swarm_agents: maxSwarmAgents,
            use_diff_transformer: useDiffTransformer,
            gpu_memory_limit_mb: gpuMemoryLimit
        });
        alert('Configuration synchronized with Omni Core.');
    };

    return (
        <div className="p-8 bg-gray-900 text-white rounded-xl shadow-2xl max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold mb-8 text-cyan-400 border-b border-gray-700 pb-4">
                Core Execution Settings
            </h2>
            
            <div className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Maximum Active Swarm Agents</label>
                    <input 
                        type="range" 
                        min="1" max="100" 
                        value={maxSwarmAgents}
                        onChange={(e) => setMaxSwarmAgents(parseInt(e.target.value))}
                        className="w-full accent-cyan-500"
                    />
                    <p className="text-right text-cyan-300 font-bold">{maxSwarmAgents} Agents</p>
                </div>

                <div className="flex items-center justify-between bg-gray-800 p-4 rounded-lg">
                    <div>
                        <h4 className="font-semibold text-lg">Use Differential Transformer</h4>
                        <p className="text-sm text-gray-400">Enable Diff-Transformer logic to reduce attention noise.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input 
                            type="checkbox" 
                            className="sr-only peer"
                            checked={useDiffTransformer}
                            onChange={() => setUseDiffTransformer(!useDiffTransformer)}
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
                    </label>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">GPU Memory Pool Limit (MB)</label>
                    <input 
                        type="number" 
                        value={gpuMemoryLimit}
                        onChange={(e) => setGpuMemoryLimit(parseInt(e.target.value))}
                        className="w-full p-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:ring-2 focus:ring-cyan-500 outline-none"
                    />
                </div>

                <button 
                    onClick={handleSave}
                    className="w-full py-4 mt-8 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 rounded-lg font-bold text-lg transition-all shadow-lg hover:shadow-cyan-500/50"
                >
                    Synchronize Configuration
                </button>
            </div>
        </div>
    );
};
