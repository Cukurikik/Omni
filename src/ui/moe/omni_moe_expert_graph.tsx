import React, { useEffect, useRef, useState } from 'react';

// OMNI MOTHER Production Zero-Mock Expert Routing Graph
// Renders dynamic, physics-based network topology of MoE experts receiving traffic.

interface ExpertNode {
  id: string;
  loadPercent: number;
  isActive: boolean;
}

interface Edge {
  source: string;
  target: string;
  trafficWeight: number; // 0 to 1
}

interface GraphProps {
  nodes: ExpertNode[];
  edges: Edge[];
}

export const MoEExpertGraph: React.FC<GraphProps> = ({ nodes, edges }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    const width = canvas.width;
    const height = canvas.height;
    
    // Physics Simulation State
    const particles: { x: number, y: number, vx: number, vy: number, node: ExpertNode }[] = nodes.map((n, i) => ({
      x: width/2 + Math.cos(i) * 100,
      y: height/2 + Math.sin(i) * 100,
      vx: 0,
      vy: 0,
      node: n
    }));

    const render = () => {
      ctx.fillStyle = 'rgba(10, 10, 15, 0.3)'; // Trailing effect
      ctx.fillRect(0, 0, width, height);

      // Simple spring physics
      particles.forEach(p => {
        // Pull to center
        p.vx += (width/2 - p.x) * 0.001;
        p.vy += (height/2 - p.y) * 0.001;
        
        // Repel from others
        particles.forEach(p2 => {
          if (p === p2) return;
          const dx = p.x - p2.x;
          const dy = p.y - p2.y;
          const dist = Math.sqrt(dx*dx + dy*dy);
          if (dist > 0 && dist < 150) {
            p.vx += (dx / dist) * 0.5;
            p.vy += (dy / dist) * 0.5;
          }
        });
        
        // Dampening
        p.vx *= 0.9;
        p.vy *= 0.9;
        
        p.x += p.vx;
        p.y += p.vy;
      });

      // Draw Edges
      edges.forEach(edge => {
        const sourceP = particles.find(p => p.node.id === edge.source);
        const targetP = particles.find(p => p.node.id === edge.target);
        if (sourceP && targetP) {
          ctx.beginPath();
          ctx.moveTo(sourceP.x, sourceP.y);
          ctx.lineTo(targetP.x, targetP.y);
          ctx.strokeStyle = `rgba(0, 255, 200, ${edge.trafficWeight})`;
          ctx.lineWidth = edge.trafficWeight * 5;
          ctx.stroke();
        }
      });

      // Draw Nodes
      particles.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 20 + p.node.loadPercent * 20, 0, Math.PI * 2);
        ctx.fillStyle = p.node.isActive ? '#00ffcc' : '#555';
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        ctx.fillStyle = '#fff';
        ctx.font = '12px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(p.node.id, p.x, p.y + 4);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [nodes, edges]);

  return (
    <div style={{ padding: '20px', borderRadius: '8px', background: '#0a0a0f', boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}>
      <h3 style={{ color: '#fff', fontFamily: 'Inter, sans-serif', margin: '0 0 15px 0' }}>Expert Topology Routing</h3>
      <canvas 
        ref={canvasRef} 
        width={600} 
        height={400} 
        style={{ width: '100%', height: '400px', background: '#050508', borderRadius: '4px' }}
      />
    </div>
  );
};
