import React, { useRef, useEffect } from 'react';

// OMNI Ploomber - DAG Pipeline Visualizer
// React/TSX Canvas Component for drawing directed acyclic graphs

interface DAGNode {
    id: string;
    label: string;
    x: number;
    y: number;
}

interface DAGEdge {
    source: string;
    target: string;
}

interface PipelineVisualizerProps {
    nodes: DAGNode[];
    edges: DAGEdge[];
    width?: number;
    height?: number;
}

export const PipelineVisualizer: React.FC<PipelineVisualizerProps> = ({ nodes, edges, width = 800, height = 600 }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, width, height);

        // Draw Edges
        ctx.strokeStyle = '#64748b'; // slate-500
        ctx.lineWidth = 2;

        edges.forEach(edge => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);

            if (sourceNode && targetNode) {
                // Arrow math
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const angle = Math.atan2(dy, dx);
                
                // Radius padding for node circle (assume radius 25)
                const padding = 25;
                const targetX = targetNode.x - padding * Math.cos(angle);
                const targetY = targetNode.y - padding * Math.sin(angle);

                ctx.beginPath();
                ctx.moveTo(sourceNode.x, sourceNode.y);
                ctx.lineTo(targetX, targetY);
                ctx.stroke();

                // Draw arrowhead
                const headlen = 10;
                ctx.beginPath();
                ctx.moveTo(targetX, targetY);
                ctx.lineTo(targetX - headlen * Math.cos(angle - Math.PI / 6), targetY - headlen * Math.sin(angle - Math.PI / 6));
                ctx.lineTo(targetX - headlen * Math.cos(angle + Math.PI / 6), targetY - headlen * Math.sin(angle + Math.PI / 6));
                ctx.lineTo(targetX, targetY);
                ctx.fillStyle = '#64748b';
                ctx.fill();
            }
        });

        // Draw Nodes
        nodes.forEach(node => {
            ctx.beginPath();
            ctx.arc(node.x, node.y, 25, 0, 2 * Math.PI, false);
            ctx.fillStyle = '#1e293b'; // slate-800
            ctx.fill();
            ctx.lineWidth = 3;
            ctx.strokeStyle = '#38bdf8'; // sky-400
            ctx.stroke();

            // Label
            ctx.fillStyle = '#f8fafc'; // slate-50
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(node.label, node.x, node.y);
        });

    }, [nodes, edges, width, height]);

    return (
        <div className="bg-slate-950 p-6 rounded-2xl shadow-xl border border-slate-800">
            <h3 className="text-2xl font-bold text-sky-400 mb-4">Pipeline Topology Graph</h3>
            <div className="overflow-x-auto">
                <canvas 
                    ref={canvasRef} 
                    width={width} 
                    height={height} 
                    className="bg-slate-900 rounded-xl"
                />
            </div>
        </div>
    );
};
