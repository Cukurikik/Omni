import React, { useEffect, useRef } from 'react';

// OmniNetworkTraffic.tsx — Real-Time Bandwidth Monitor
// Layer: Interface / TypeScript
//
// Renders a dual-line scrolling chart tracking incoming (RX) and outgoing (TX)
// network traffic. Uses Canvas 2D for high-fps rendering of high-density data. Zero mock.

export interface OmniTrafficData {
    timestamp: number; // Unix epoch ms
    rxBytes: number;
    txBytes: number;
}

export interface OmniNetworkTrafficProps {
    data: OmniTrafficData[];
    width: number;
    height: number;
    maxWindowMs?: number; // e.g., 60000 for 1 minute window
    className?: string;
}

export const OmniNetworkTraffic: React.FC<OmniNetworkTrafficProps> = ({
    data,
    width,
    height,
    maxWindowMs = 60000,
    className = ''
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const draw = () => {
            // 1. Clear Canvas
            ctx.clearRect(0, 0, width, height);

            if (data.length === 0) {
                requestRef.current = requestAnimationFrame(draw);
                return;
            }

            // 2. Determine time bounds
            const now = Date.now();
            const minTime = now - maxWindowMs;

            // Filter data to only what's visible
            const visibleData = data.filter(d => d.timestamp >= minTime);
            if (visibleData.length === 0) {
                requestRef.current = requestAnimationFrame(draw);
                return;
            }

            // 3. Determine value bounds (Y axis scaling)
            let maxBytes = 100; // Minimum scale
            for (let i = 0; i < visibleData.length; i++) {
                if (visibleData[i].rxBytes > maxBytes) maxBytes = visibleData[i].rxBytes;
                if (visibleData[i].txBytes > maxBytes) maxBytes = visibleData[i].txBytes;
            }
            // Add 10% padding to top
            maxBytes *= 1.1;

            // 4. Drawing Helpers
            const getX = (ts: number) => {
                return ((ts - minTime) / maxWindowMs) * width;
            };

            const getY = (val: number) => {
                return height - ((val / maxBytes) * height);
            };

            const drawLine = (key: 'rxBytes' | 'txBytes', color: string, fill: string) => {
                ctx.beginPath();
                ctx.moveTo(getX(visibleData[0].timestamp), getY(visibleData[0][key]));

                for (let i = 1; i < visibleData.length; i++) {
                    ctx.lineTo(getX(visibleData[i].timestamp), getY(visibleData[i][key]));
                }

                // Fill area under line
                const lastX = getX(visibleData[visibleData.length - 1].timestamp);
                const firstX = getX(visibleData[0].timestamp);
                
                ctx.lineTo(lastX, height);
                ctx.lineTo(firstX, height);
                ctx.closePath();

                ctx.fillStyle = fill;
                ctx.fill();

                // Re-trace the line for stroke
                ctx.beginPath();
                ctx.moveTo(getX(visibleData[0].timestamp), getY(visibleData[0][key]));
                for (let i = 1; i < visibleData.length; i++) {
                    ctx.lineTo(getX(visibleData[i].timestamp), getY(visibleData[i][key]));
                }

                ctx.strokeStyle = color;
                ctx.lineWidth = 2;
                ctx.lineJoin = 'round';
                ctx.stroke();
            };

            // Draw TX (Outgoing - Blue)
            drawLine('txBytes', '#3b82f6', 'rgba(59, 130, 246, 0.2)');
            
            // Draw RX (Incoming - Emerald)
            drawLine('rxBytes', '#10b981', 'rgba(16, 185, 129, 0.2)');

            requestRef.current = requestAnimationFrame(draw);
        };

        requestRef.current = requestAnimationFrame(draw);

        return () => {
            if (requestRef.current) {
                cancelAnimationFrame(requestRef.current);
            }
        };
    }, [data, width, height, maxWindowMs]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-md bg-slate-900 border border-slate-700 ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Network Traffic Monitor"
        />
    );
};
