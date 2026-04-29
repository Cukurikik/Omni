import React from 'react';

// OMNI DIGITS: Model Topology Viewer
// React TSX component to render directed graph layouts of Deep Neural Networks (CNNs).
// Source: NVIDIA/DIGITS

interface LayerNode {
    id: string;
    type: 'Convolution' | 'Pooling' | 'InnerProduct' | 'ReLU' | 'Softmax';
    name: string;
    params?: Record<string, any>;
}

interface LayerConnection {
    source: string;
    target: string;
}

interface ModelViewerProps {
    modelName: string;
    layers: LayerNode[];
    connections: LayerConnection[];
}

export const ModelViewer: React.FC<ModelViewerProps> = ({ modelName, layers, connections }) => {
    
    // Very basic vertical layout algorithm for standard CNN feeds
    const renderGraph = () => {
        let currentY = 50;
        const nodePositions: Record<string, { x: number, y: number }> = {};
        
        // Calculate positions (Assuming mostly sequential for this simple renderer)
        layers.forEach((layer) => {
            nodePositions[layer.id] = { x: 300, y: currentY };
            currentY += 100;
        });

        return (
            <svg width="600" height={currentY} style={{ backgroundColor: '#1e1e1e' }}>
                {/* Render Edges */}
                {connections.map((conn, idx) => {
                    const src = nodePositions[conn.source];
                    const tgt = nodePositions[conn.target];
                    if (!src || !tgt) return null;
                    return (
                        <line 
                            key={`edge-${idx}`}
                            x1={src.x} y1={src.y + 20} 
                            x2={tgt.x} y2={tgt.y - 20} 
                            stroke="#5cb85c" 
                            strokeWidth="2" 
                            markerEnd="url(#arrowhead)"
                        />
                    );
                })}
                
                {/* Render Nodes */}
                {layers.map(layer => {
                    const pos = nodePositions[layer.id];
                    return (
                        <g key={layer.id} transform={`translate(${pos.x}, ${pos.y})`}>
                            <rect 
                                x="-75" y="-20" width="150" height="40" 
                                rx="5" ry="5" 
                                fill="#2c3e50" 
                                stroke="#34495e" strokeWidth="2"
                            />
                            <text 
                                x="0" y="5" 
                                fill="white" 
                                textAnchor="middle" 
                                fontFamily="monospace" fontSize="12"
                            >
                                {layer.name} ({layer.type})
                            </text>
                        </g>
                    );
                })}
                
                {/* Arrow Definition */}
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                      <polygon points="0 0, 10 3.5, 0 7" fill="#5cb85c" />
                    </marker>
                </defs>
            </svg>
        );
    };

    return (
        <div className="omni-model-viewer">
            <h3 style={{ color: '#ecf0f1', fontFamily: 'sans-serif' }}>Topology: {modelName}</h3>
            {renderGraph()}
        </div>
    );
};
