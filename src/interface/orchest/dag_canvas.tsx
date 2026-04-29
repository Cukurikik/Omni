import React, { useState, useCallback } from 'react';

// OMNI ORCHEST: Pipeline DAG Canvas
// React/TypeScript representation of machine learning data pipelines.
// Source: orchest/orchest

interface NodeData {
    id: string;
    label: string;
    type: 'step' | 'source' | 'sink';
    x: number;
    y: number;
}

interface EdgeData {
    id: string;
    source: string;
    target: string;
}

interface DagCanvasProps {
    initialNodes: NodeData[];
    initialEdges: EdgeData[];
    onNodeExecute: (id: string) => void;
}

export const DagCanvas: React.FC<DagCanvasProps> = ({ initialNodes, initialEdges, onNodeExecute }) => {
    const [nodes, setNodes] = useState<NodeData[]>(initialNodes);
    const [edges, setEdges] = useState<EdgeData[]>(initialEdges);
    const [selectedNode, setSelectedNode] = useState<string | null>(null);

    const handleNodeClick = useCallback((id: string) => {
        setSelectedNode(id);
    }, []);

    const handleExecuteClick = () => {
        if (selectedNode) {
            onNodeExecute(selectedNode);
        }
    };

    return (
        <div className="omni-dag-container" style={{ position: 'relative', width: '100%', height: '600px', backgroundColor: '#1e1e1e' }}>
            {/* SVG Layer for Edges */}
            <svg style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
                {edges.map(edge => {
                    const sourceNode = nodes.find(n => n.id === edge.source);
                    const targetNode = nodes.find(n => n.id === edge.target);
                    if (!sourceNode || !targetNode) return null;
                    
                    return (
                        <line 
                            key={edge.id}
                            x1={sourceNode.x + 50} 
                            y1={sourceNode.y + 25} 
                            x2={targetNode.x + 50} 
                            y2={targetNode.y + 25} 
                            stroke="#555" 
                            strokeWidth={2}
                        />
                    );
                })}
            </svg>

            {/* DOM Layer for Nodes */}
            {nodes.map(node => (
                <div 
                    key={node.id}
                    onClick={() => handleNodeClick(node.id)}
                    style={{
                        position: 'absolute',
                        left: node.x,
                        top: node.y,
                        width: '100px',
                        height: '50px',
                        backgroundColor: selectedNode === node.id ? '#4a90e2' : '#333',
                        color: 'white',
                        border: '1px solid #555',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        cursor: 'pointer',
                        boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
                        userSelect: 'none'
                    }}
                >
                    {node.label}
                </div>
            ))}

            {/* Control Panel */}
            <div style={{ position: 'absolute', bottom: 20, right: 20, backgroundColor: '#222', padding: '10px', borderRadius: '8px' }}>
                <p style={{ color: 'white', margin: '0 0 10px 0' }}>Selected: {selectedNode || 'None'}</p>
                <button 
                    onClick={handleExecuteClick}
                    disabled={!selectedNode}
                    style={{
                        backgroundColor: selectedNode ? '#2ecc71' : '#555',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        cursor: selectedNode ? 'pointer' : 'not-allowed'
                    }}
                >
                    Execute Step
                </button>
            </div>
        </div>
    );
};
