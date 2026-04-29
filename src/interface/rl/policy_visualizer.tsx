import React, { useEffect, useRef } from 'react';

// OMNI RL - Policy Value Map Visualizer
// Strict TypeScript types, React functional component for monitoring RL training.

interface PolicyState {
    x: number;
    y: number;
    value: number;
}

interface VisualizerProps {
    policyMap: PolicyState[];
    width?: number;
    height?: number;
}

export const PolicyVisualizer: React.FC<VisualizerProps> = ({ policyMap, width = 400, height = 400 }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Clear canvas
        ctx.clearRect(0, 0, width, height);

        // Find min and max for normalization
        let minVal = Infinity;
        let maxVal = -Infinity;
        policyMap.forEach(p => {
            if (p.value < minVal) minVal = p.value;
            if (p.value > maxVal) maxVal = p.value;
        });

        // Prevent division by zero
        if (maxVal === minVal) maxVal = minVal + 1;

        // Draw map
        const gridSize = 20; // Assuming grid size
        policyMap.forEach(p => {
            const normalized = (p.value - minVal) / (maxVal - minVal);
            // Color map: low=red, high=green
            const r = Math.round(255 * (1 - normalized));
            const g = Math.round(255 * normalized);
            const b = 0;

            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(p.x * gridSize, p.y * gridSize, gridSize, gridSize);
        });
    }, [policyMap, width, height]);

    return (
        <div className="p-4 bg-gray-900 rounded-lg shadow-lg">
            <h3 className="text-xl font-bold text-white mb-4">RL Policy Value Map</h3>
            <canvas 
                ref={canvasRef} 
                width={width} 
                height={height} 
                className="border border-gray-700 bg-black"
            />
        </div>
    );
};
