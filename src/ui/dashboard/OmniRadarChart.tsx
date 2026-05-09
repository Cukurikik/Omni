import React, { useEffect, useRef } from 'react';

// OmniRadarChart.tsx — Radar / Spider Web Chart
// Layer: Interface / TypeScript
//
// Renders a high-performance Canvas 2D Radar Chart for multi-dimensional 
// data comparison (e.g., skill attributes, AI model benchmarks). Zero mock.

export interface OmniRadarData {
    label: string;
    value: number; // Normalized 0.0 to 1.0
}

export interface OmniRadarChartProps {
    data: OmniRadarData[];
    width: number;
    height: number;
    fillColor?: string;
    strokeColor?: string;
    gridLevels?: number;
    className?: string;
}

export const OmniRadarChart: React.FC<OmniRadarChartProps> = ({
    data,
    width,
    height,
    fillColor = 'rgba(59, 130, 246, 0.4)', // Tailwind blue-500 with opacity
    strokeColor = '#3b82f6',
    gridLevels = 5,
    className = ''
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const cx = width / 2;
        const cy = height / 2;
        const radius = Math.min(cx, cy) * 0.8;
        const numPoints = data.length;
        const angleStep = (Math.PI * 2) / numPoints;

        // Clear Canvas
        ctx.clearRect(0, 0, width, height);

        // 1. Draw Grid Web
        ctx.strokeStyle = '#334155'; // slate-700
        ctx.lineWidth = 1;

        for (let level = 1; level <= gridLevels; level++) {
            const r = radius * (level / gridLevels);
            ctx.beginPath();
            for (let i = 0; i < numPoints; i++) {
                const angle = i * angleStep - Math.PI / 2; // Start at top
                const x = cx + Math.cos(angle) * r;
                const y = cy + Math.sin(angle) * r;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.closePath();
            ctx.stroke();
        }

        // 2. Draw Axis Lines
        for (let i = 0; i < numPoints; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const x = cx + Math.cos(angle) * radius;
            const y = cy + Math.sin(angle) * radius;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(x, y);
            ctx.stroke();
            
            // Draw Labels
            ctx.fillStyle = '#cbd5e1'; // slate-300
            ctx.font = '10px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Offset label slightly outside the radius
            const lx = cx + Math.cos(angle) * (radius * 1.15);
            const ly = cy + Math.sin(angle) * (radius * 1.15);
            ctx.fillText(data[i].label, lx, ly);
        }

        // 3. Draw Data Polygon
        ctx.beginPath();
        for (let i = 0; i < numPoints; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const val = Math.max(0, Math.min(1, data[i].value)); // Clamp 0-1
            const r = radius * val;
            const x = cx + Math.cos(angle) * r;
            const y = cy + Math.sin(angle) * r;
            
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();

        // Fill and Stroke Data Polygon
        ctx.fillStyle = fillColor;
        ctx.fill();
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;
        ctx.stroke();

        // 4. Draw Data Points
        ctx.fillStyle = '#ffffff';
        for (let i = 0; i < numPoints; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const val = Math.max(0, Math.min(1, data[i].value));
            const r = radius * val;
            const x = cx + Math.cos(angle) * r;
            const y = cy + Math.sin(angle) * r;
            
            ctx.beginPath();
            ctx.arc(x, y, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }

    }, [data, width, height, fillColor, strokeColor, gridLevels]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-lg bg-slate-900 ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Radar Chart"
        />
    );
};
