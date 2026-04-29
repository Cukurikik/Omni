import React, { useState, useEffect } from 'react';

// OMNI DEEPSPEED: GPU Memory & Utilization Dashboard
// Visualizes ZeRO stages, memory fragmentation, and TFLOPs across a distributed cluster.
// Source: microsoft/DeepSpeed

interface GpuState {
    rank: number;
    memoryAllocatedGb: number;
    memoryTotalGb: number;
    utilizationPercent: number;
    stage: string; // ZeRO 1, 2, 3
}

export const GpuDashboard: React.FC = () => {
    // Simulated state for structural UI
    const [gpus, setGpus] = useState<GpuState[]>([
        { rank: 0, memoryAllocatedGb: 35.2, memoryTotalGb: 40, utilizationPercent: 98, stage: "ZeRO-3" },
        { rank: 1, memoryAllocatedGb: 35.1, memoryTotalGb: 40, utilizationPercent: 97, stage: "ZeRO-3" },
        { rank: 2, memoryAllocatedGb: 35.4, memoryTotalGb: 40, utilizationPercent: 99, stage: "ZeRO-3" },
        { rank: 3, memoryAllocatedGb: 35.0, memoryTotalGb: 40, utilizationPercent: 95, stage: "ZeRO-3" },
    ]);

    return (
        <div style={{ padding: '20px', backgroundColor: '#1e1e2f', color: '#e0e0e0', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
            <h1 style={{ borderBottom: '2px solid #4caf50', paddingBottom: '10px' }}>DeepSpeed Cluster Telemetry</h1>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '20px' }}>
                {gpus.map(gpu => {
                    const memPercent = (gpu.memoryAllocatedGb / gpu.memoryTotalGb) * 100;
                    return (
                        <div key={gpu.rank} style={{ backgroundColor: '#2a2a40', padding: '15px', borderRadius: '8px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                            <h3 style={{ margin: '0 0 15px 0', color: '#4caf50' }}>Rank {gpu.rank} <span style={{fontSize: '0.8em', color: '#aaa'}}>({gpu.stage})</span></h3>
                            
                            <div style={{ marginBottom: '10px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                                    <span>VRAM: {gpu.memoryAllocatedGb.toFixed(1)} GB / {gpu.memoryTotalGb} GB</span>
                                    <span>{memPercent.toFixed(1)}%</span>
                                </div>
                                <div style={{ width: '100%', height: '10px', backgroundColor: '#1e1e2f', borderRadius: '5px', overflow: 'hidden', marginTop: '5px' }}>
                                    <div style={{ width: `${memPercent}%`, height: '100%', backgroundColor: memPercent > 90 ? '#f44336' : '#2196f3' }} />
                                </div>
                            </div>

                            <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9em' }}>
                                    <span>Compute Utilization</span>
                                    <span>{gpu.utilizationPercent}%</span>
                                </div>
                                <div style={{ width: '100%', height: '10px', backgroundColor: '#1e1e2f', borderRadius: '5px', overflow: 'hidden', marginTop: '5px' }}>
                                    <div style={{ width: `${gpu.utilizationPercent}%`, height: '100%', backgroundColor: '#4caf50' }} />
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
