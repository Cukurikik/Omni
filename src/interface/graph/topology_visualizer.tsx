import React, { useState, useEffect, useRef } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface Node {
    id: string;
    x: number;
    y: number;
    value: number; // e.g., PageRank score
}

interface Edge {
    source: string;
    target: string;
}

export const TopologyVisualizer: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [isSimulating, setIsSimulating] = useState(true);

    useEffect(() => {
        // Initialize random graph topology
        const initNodes: Node[] = Array.from({ length: 50 }, (_, i) => ({
            id: `n${i}`,
            x: Math.random() * 800,
            y: Math.random() * 600,
            value: Math.random()
        }));

        const initEdges: Edge[] = [];
        for (let i = 0; i < 75; i++) {
            const source = initNodes[Math.floor(Math.random() * initNodes.length)].id;
            const target = initNodes[Math.floor(Math.random() * initNodes.length)].id;
            if (source !== target) {
                initEdges.push({ source, target });
            }
        }

        setNodes(initNodes);
        setEdges(initEdges);
    }, []);

    useEffect(() => {
        if (!isSimulating || nodes.length === 0) return;

        let animationFrameId: number;
        let currentNodes = [...nodes];

        const simulateForceLayout = () => {
            // Simplified force-directed layout step
            const updatedNodes = currentNodes.map(node => {
                let dx = 0;
                let dy = 0;

                // Repulsion
                currentNodes.forEach(other => {
                    if (node.id === other.id) return;
                    const distSq = Math.max(1, Math.pow(node.x - other.x, 2) + Math.pow(node.y - other.y, 2));
                    const force = 1000 / distSq;
                    dx += (node.x - other.x) * force * 0.01;
                    dy += (node.y - other.y) * force * 0.01;
                });

                // Attraction (Edges)
                edges.forEach(edge => {
                    if (edge.source === node.id || edge.target === node.id) {
                        const otherId = edge.source === node.id ? edge.target : edge.source;
                        const other = currentNodes.find(n => n.id === otherId);
                        if (other) {
                            dx -= (node.x - other.x) * 0.05;
                            dy -= (node.y - other.y) * 0.05;
                        }
                    }
                });

                // Center gravity
                dx += (400 - node.x) * 0.01;
                dy += (300 - node.y) * 0.01;

                return {
                    ...node,
                    x: Math.max(20, Math.min(780, node.x + dx)),
                    y: Math.max(20, Math.min(580, node.y + dy))
                };
            });

            currentNodes = updatedNodes;
            drawGraph(updatedNodes, edges);
            animationFrameId = requestAnimationFrame(simulateForceLayout);
        };

        simulateForceLayout();
        return () => cancelAnimationFrame(animationFrameId);
    }, [isSimulating, nodes.length, edges]);

    const drawGraph = (ns: Node[], es: Edge[]) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw edges
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        es.forEach(edge => {
            const sourceNode = ns.find(n => n.id === edge.source);
            const targetNode = ns.find(n => n.id === edge.target);
            if (sourceNode && targetNode) {
                ctx.beginPath();
                ctx.moveTo(sourceNode.x, sourceNode.y);
                ctx.lineTo(targetNode.x, targetNode.y);
                ctx.stroke();
            }
        });

        // Draw nodes
        ns.forEach(node => {
            const radius = 5 + (node.value * 10);
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI);
            ctx.fillStyle = `hsl(${200 + node.value * 100}, 80%, 60%)`;
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        });
    };

    return (
        <div style={{ backgroundColor: '#020617', padding: '24px', borderRadius: '12px', color: '#f8fafc', fontFamily: 'sans-serif' }}>
            <h2 style={{ color: '#38bdf8', marginTop: 0 }}>Graph Topology Visualizer</h2>
            <div style={{ marginBottom: '16px', display: 'flex', gap: '12px' }}>
                <button 
                    onClick={() => setIsSimulating(!isSimulating)}
                    style={{ backgroundColor: isSimulating ? '#ef4444' : '#10b981', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}
                >
                    {isSimulating ? 'Pause Physics' : 'Resume Physics'}
                </button>
            </div>
            
            <div style={{ border: '1px solid #1e293b', borderRadius: '8px', overflow: 'hidden', width: '800px', height: '600px', backgroundColor: '#0f172a' }}>
                <canvas 
                    ref={canvasRef} 
                    width={800} 
                    height={600}
                    style={{ display: 'block' }}
                />
            </div>
            
            <div style={{ marginTop: '16px', color: '#94a3b8', fontSize: '14px' }}>
                Vertices: {nodes.length} | Edges: {edges.length} | Algorithm: Fruchterman-Reingold Force-Directed
            </div>
        </div>
    );
};
