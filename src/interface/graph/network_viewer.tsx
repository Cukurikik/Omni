import React, { useEffect, useRef, useState } from 'react';

export interface GraphNode {
    id: string;
    label: string;
    group: number;
    val: number;
}

export interface GraphLink {
    source: string;
    target: string;
    value: number;
}

interface NetworkViewerProps {
    nodes: GraphNode[];
    links: GraphLink[];
    width: number;
    height: number;
}

export const OmniNetworkViewer: React.FC<NetworkViewerProps> = ({ nodes, links, width, height }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            setError('Failed to acquire 2D rendering context.');
            return;
        }

        try {
            // Structural mock for force-directed rendering.
            // In a full production TSX without external libraries, we implement a basic Euler integration force layout.
            
            // 1. Initialize positions randomly
            const positions = new Map<string, { x: number, y: number, vx: number, vy: number }>();
            nodes.forEach(n => {
                positions.set(n.id, {
                    x: Math.random() * width,
                    y: Math.random() * height,
                    vx: 0,
                    vy: 0
                });
            });

            // Very basic layout pass (1 iteration for static render, usually this is animated)
            const k = Math.sqrt((width * height) / nodes.length); // Optimal distance
            const attraction = 0.01;
            const repulsion = 100.0;
            
            // Fruchterman-Reingold inspired single pass for structure
            for (let iter = 0; iter < 50; iter++) {
                // Repulsion
                nodes.forEach(v => {
                    nodes.forEach(u => {
                        if (v.id !== u.id) {
                            const pv = positions.get(v.id)!;
                            const pu = positions.get(u.id)!;
                            const dx = pv.x - pu.x;
                            const dy = pv.y - pu.y;
                            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                            const force = (repulsion * repulsion) / dist;
                            pv.vx += (dx / dist) * force;
                            pv.vy += (dy / dist) * force;
                        }
                    });
                });

                // Attraction
                links.forEach(link => {
                    const ps = positions.get(link.source);
                    const pt = positions.get(link.target);
                    if (ps && pt) {
                        const dx = ps.x - pt.x;
                        const dy = ps.y - pt.y;
                        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                        const force = (dist * dist) / k;
                        ps.vx -= (dx / dist) * force * attraction;
                        ps.vy -= (dy / dist) * force * attraction;
                        pt.vx += (dx / dist) * force * attraction;
                        pt.vy += (dy / dist) * force * attraction;
                    }
                });

                // Update
                nodes.forEach(n => {
                    const p = positions.get(n.id)!;
                    // Cap velocity and update
                    p.x += Math.max(-10, Math.min(10, p.vx));
                    p.y += Math.max(-10, Math.min(10, p.vy));
                    
                    // Boundary constraint
                    p.x = Math.max(10, Math.min(width - 10, p.x));
                    p.y = Math.max(10, Math.min(height - 10, p.y));
                    
                    p.vx = 0; p.vy = 0;
                });
            }

            // Rendering
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);

            // Draw Links
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 1;
            links.forEach(link => {
                const ps = positions.get(link.source);
                const pt = positions.get(link.target);
                if (ps && pt) {
                    ctx.beginPath();
                    ctx.moveTo(ps.x, ps.y);
                    ctx.lineTo(pt.x, pt.y);
                    ctx.stroke();
                }
            });

            // Draw Nodes
            const colors = ['#f43f5e', '#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'];
            nodes.forEach(n => {
                const p = positions.get(n.id);
                if (p) {
                    ctx.beginPath();
                    ctx.arc(p.x, p.y, Math.sqrt(n.val) * 2 + 2, 0, Math.PI * 2);
                    ctx.fillStyle = colors[n.group % colors.length];
                    ctx.fill();
                    ctx.strokeStyle = '#0f172a';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }
            });

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown rendering error');
        }

    }, [nodes, links, width, height]);

    return (
        <div className="omni-network-viewer border border-slate-700 rounded-lg overflow-hidden shadow-2xl">
            {error ? (
                <div className="p-4 text-red-400 font-mono text-sm">Error: {error}</div>
            ) : (
                <canvas ref={canvasRef} width={width} height={height} className="block cursor-grab" />
            )}
        </div>
    );
};
