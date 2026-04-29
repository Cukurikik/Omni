import React, { useEffect, useState, useRef } from 'react';

// OMNI RL - Live Reward Curve Plotter
// High-performance canvas-based React visualizer for training metrics

interface DataPoint {
    episode: number;
    reward: number;
}

interface PlotterProps {
    data: DataPoint[];
    width?: number;
    height?: number;
}

export const RewardPlotter: React.FC<PlotterProps> = ({ data, width = 600, height = 300 }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, width, height);

        if (data.length === 0) return;

        const padding = 40;
        const plotWidth = width - padding * 2;
        const plotHeight = height - padding * 2;

        const maxEpisode = Math.max(...data.map(d => d.episode));
        const maxReward = Math.max(...data.map(d => d.reward));
        const minReward = Math.min(...data.map(d => d.reward));

        // Draw axes
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(padding, padding);
        ctx.lineTo(padding, height - padding);
        ctx.lineTo(width - padding, height - padding);
        ctx.stroke();

        // Plot line
        ctx.strokeStyle = '#3b82f6'; // Blue-500
        ctx.lineWidth = 2;
        ctx.beginPath();

        data.forEach((point, index) => {
            const x = padding + (point.episode / maxEpisode) * plotWidth;
            const range = maxReward - minReward === 0 ? 1 : maxReward - minReward;
            const y = (height - padding) - ((point.reward - minReward) / range) * plotHeight;

            if (index === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        });

        ctx.stroke();
    }, [data, width, height]);

    return (
        <div className="bg-slate-900 p-4 rounded-xl shadow-2xl border border-slate-700">
            <h3 className="text-xl font-bold text-slate-100 mb-2">Training Reward Curve</h3>
            <canvas 
                ref={canvasRef} 
                width={width} 
                height={height} 
                className="bg-slate-800 rounded-lg"
            />
        </div>
    );
};
