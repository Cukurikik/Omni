import React, { useEffect, useRef, useState } from 'react';

interface DendrogramNode {
    id: number;
    parent_id: number | null;
    lambda_val: number;
    child_size: number;
    is_cluster: boolean;
}

interface OmniDendrogramProps {
    treeData: DendrogramNode[];
    width: number;
    height: number;
    onNodeSelect: (id: number) => void;
}

export const OmniDendrogramView: React.FC<OmniDendrogramProps> = ({ treeData, width, height, onNodeSelect }) => {
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
            // Clear canvas
            ctx.clearRect(0, 0, width, height);
            
            // Set dark theme background
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(0, 0, width, height);

            if (treeData.length === 0) {
                ctx.fillStyle = '#94a3b8';
                ctx.font = '14px Inter, sans-serif';
                ctx.fillText('No tree data available to render.', 20, 30);
                return;
            }

            // Find bounds for normalization
            let maxLambda = 0;
            let maxDepth = 0;
            
            // Calculate depths (simplified tree parsing)
            const nodeMap = new Map<number, DendrogramNode>();
            treeData.forEach(n => {
                nodeMap.set(n.id, n);
                if (n.lambda_val > maxLambda) maxLambda = n.lambda_val;
            });

            // Drawing parameters
            const marginX = 40;
            const marginY = 40;
            const drawWidth = width - (marginX * 2);
            const drawHeight = height - (marginY * 2);

            // Render root down
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 1.5;

            // Simplified rendering loop for demonstration of production structural logic
            treeData.forEach(node => {
                if (node.parent_id !== null && nodeMap.has(node.parent_id)) {
                    const parent = nodeMap.get(node.parent_id)!;
                    
                    const x1 = marginX + (parent.id % 20) * (drawWidth / 20); // Dummy structural coordinate logic
                    const y1 = marginY + (parent.lambda_val / maxLambda) * drawHeight;
                    
                    const x2 = marginX + (node.id % 20) * (drawWidth / 20);
                    const y2 = marginY + (node.lambda_val / maxLambda) * drawHeight;

                    ctx.beginPath();
                    ctx.moveTo(x1, y1);
                    ctx.lineTo(x2, y2);
                    ctx.stroke();
                }

                // Draw node
                ctx.fillStyle = node.is_cluster ? '#10b981' : '#f43f5e';
                const nodeX = marginX + (node.id % 20) * (drawWidth / 20);
                const nodeY = marginY + (node.lambda_val / maxLambda) * drawHeight;
                
                ctx.beginPath();
                ctx.arc(nodeX, nodeY, Math.max(2, Math.log2(node.child_size) * 1.5), 0, Math.PI * 2);
                ctx.fill();
            });

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown rendering error occurred.');
        }

    }, [treeData, width, height]);

    return (
        <div className="omni-dendrogram-container rounded-lg shadow-xl overflow-hidden bg-slate-900 border border-slate-700">
            {error ? (
                <div className="p-4 text-red-400 font-mono text-sm">Error: {error}</div>
            ) : (
                <canvas 
                    ref={canvasRef} 
                    width={width} 
                    height={height}
                    className="block cursor-crosshair"
                    onClick={(e) => {
                        // Dummy interactive bounds check for production
                        onNodeSelect(0); 
                    }}
                />
            )}
        </div>
    );
};
