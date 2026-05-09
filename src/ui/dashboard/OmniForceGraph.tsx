import React, { useEffect, useRef } from 'react';

// OmniForceGraph.tsx — Physics-Based Force-Directed Graph
// Layer: Interface / TypeScript
// Inspired by: d3-force
//
// Renders an interactive network graph using a simple 2D physics simulation
// (Hooke's Law for springs, Coulomb's Law for repulsion) on an HTML5 Canvas. Zero mock.

export interface OmniForceNode {
    id: string;
    x: number;
    y: number;
    vx: number;
    vy: number;
    radius: number;
    color: string;
}

export interface OmniForceLink {
    sourceId: string;
    targetId: string;
    distance: number;
}

export interface OmniForceGraphProps {
    nodes: OmniForceNode[];
    links: OmniForceLink[];
    width: number;
    height: number;
    className?: string;
}

export const OmniForceGraph: React.FC<OmniForceGraphProps> = ({
    nodes,
    links,
    width,
    height,
    className = ''
}) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const requestRef = useRef<number>();

    // Copy data to avoid mutating props directly
    const nodesRef = useRef<OmniForceNode[]>(JSON.parse(JSON.stringify(nodes)));
    
    // Create a fast lookup map for links
    const linkMap = useRef<{s: OmniForceNode, t: OmniForceNode, dist: number}[]>([]);

    useEffect(() => {
        const nodeMap = new Map<string, OmniForceNode>();
        nodesRef.current.forEach(n => nodeMap.set(n.id, n));

        linkMap.current = links.map(l => ({
            s: nodeMap.get(l.sourceId)!,
            t: nodeMap.get(l.targetId)!,
            dist: l.distance
        })).filter(l => l.s && l.t);
    }, [nodes, links]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        // Physics constants
        const REPULSION = 1000;
        const SPRING_K = 0.05;
        const DAMPING = 0.85;

        const simulate = () => {
            const currentNodes = nodesRef.current;

            // 1. Repulsion (Coulomb's Law) - O(N^2) naive
            for (let i = 0; i < currentNodes.length; i++) {
                for (let j = i + 1; j < currentNodes.length; j++) {
                    const n1 = currentNodes[i];
                    const n2 = currentNodes[j];
                    
                    let dx = n1.x - n2.x;
                    let dy = n1.y - n2.y;
                    let distSq = dx*dx + dy*dy;
                    
                    if (distSq === 0) { dx = Math.random(); dy = Math.random(); distSq = dx*dx + dy*dy; }
                    
                    const dist = Math.sqrt(distSq);
                    // Force inversely proportional to square of distance
                    const force = REPULSION / distSq; 
                    
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    
                    n1.vx += fx; n1.vy += fy;
                    n2.vx -= fx; n2.vy -= fy;
                }
            }

            // 2. Attraction (Hooke's Law for Springs)
            linkMap.current.forEach(link => {
                const dx = link.t.x - link.s.x;
                const dy = link.t.y - link.s.y;
                const dist = Math.sqrt(dx*dx + dy*dy) || 1;
                
                const force = (dist - link.dist) * SPRING_K;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                
                link.s.vx += fx; link.s.vy += fy;
                link.t.vx -= fx; link.t.vy -= fy;
            });

            // 3. Center Gravity (pulls loose nodes to middle)
            const cx = width / 2;
            const cy = height / 2;
            currentNodes.forEach(n => {
                n.vx += (cx - n.x) * 0.01;
                n.vy += (cy - n.y) * 0.01;
            });

            // 4. Update Positions & Dampen
            currentNodes.forEach(n => {
                n.vx *= DAMPING;
                n.vy *= DAMPING;
                n.x += n.vx;
                n.y += n.vy;
                
                // Boundaries
                if (n.x < n.radius) { n.x = n.radius; n.vx *= -1; }
                if (n.y < n.radius) { n.y = n.radius; n.vy *= -1; }
                if (n.x > width - n.radius) { n.x = width - n.radius; n.vx *= -1; }
                if (n.y > height - n.radius) { n.y = height - n.radius; n.vy *= -1; }
            });

            // Render
            ctx.clearRect(0, 0, width, height);

            // Draw Links
            ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)'; // slate-400
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            linkMap.current.forEach(link => {
                ctx.moveTo(link.s.x, link.s.y);
                ctx.lineTo(link.t.x, link.t.y);
            });
            ctx.stroke();

            // Draw Nodes
            currentNodes.forEach(n => {
                ctx.beginPath();
                ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
                ctx.fillStyle = n.color;
                ctx.fill();
                ctx.strokeStyle = '#fff';
                ctx.lineWidth = 2;
                ctx.stroke();
            });

            requestRef.current = requestAnimationFrame(simulate);
        };

        requestRef.current = requestAnimationFrame(simulate);

        return () => {
            if (requestRef.current) cancelAnimationFrame(requestRef.current);
        };
    }, [width, height]);

    return (
        <canvas
            ref={canvasRef}
            width={width}
            height={height}
            className={`rounded-xl shadow-md bg-slate-50 ${className}`}
            style={{ width: `${width}px`, height: `${height}px` }}
            aria-label="Interactive Force-Directed Graph"
        />
    );
};
