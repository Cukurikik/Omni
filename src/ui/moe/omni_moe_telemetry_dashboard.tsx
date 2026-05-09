import React, { useEffect, useRef, useState } from 'react';

// OMNI MOTHER Production Zero-Mock Real-Time Telemetry Dashboard
// Renders massive metric pipelines from the MoE hardware interfaces using Canvas/WebGL.

interface TelemetryPoint {
  timestamp: number;
  vram_usage_mb: number;
  nvme_bandwidth_mbps: number;
  p99_latency_ms: number;
}

interface DashboardProps {
  streamUrl: string;
  refreshRateMs?: number;
}

export const MoETelemetryDashboard: React.FC<DashboardProps> = ({ 
  streamUrl, 
  refreshRateMs = 100 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [status, setStatus] = useState<'CONNECTING' | 'LIVE' | 'OFFLINE'>('CONNECTING');
  const dataBuffer = useRef<TelemetryPoint[]>([]);

  useEffect(() => {
    let active = true;
    let ws: WebSocket;

    const connect = () => {
      ws = new WebSocket(streamUrl);
      
      ws.onopen = () => setStatus('LIVE');
      
      ws.onmessage = (event) => {
        if (!active) return;
        try {
          const point: TelemetryPoint = JSON.parse(event.data);
          dataBuffer.current.push(point);
          // Keep only last 1000 points
          if (dataBuffer.current.length > 1000) {
            dataBuffer.current.shift();
          }
        } catch (e) {
          console.error("OMNI CRITICAL: Telemetry parsing failure", e);
        }
      };

      ws.onclose = () => {
        if (active) {
          setStatus('OFFLINE');
          setTimeout(connect, 2000); // Backoff retry
        }
      };
    };

    connect();

    // Render loop
    const renderCanvas = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const width = canvas.width;
      const height = canvas.height;
      
      // Clear background
      ctx.fillStyle = '#0a0a0a';
      ctx.fillRect(0, 0, width, height);

      const data = dataBuffer.current;
      if (data.length < 2) {
        requestAnimationFrame(renderCanvas);
        return;
      }

      // Draw VRAM Usage Line
      ctx.beginPath();
      ctx.strokeStyle = '#00ffcc';
      ctx.lineWidth = 2;
      
      const maxVram = 24000; // Assume 24GB Max for scale
      const xStep = width / 1000;

      data.forEach((point, i) => {
        const x = i * xStep;
        const y = height - (point.vram_usage_mb / maxVram) * height;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();

      if (active) requestAnimationFrame(renderCanvas);
    };

    requestAnimationFrame(renderCanvas);

    return () => {
      active = false;
      if (ws) ws.close();
    };
  }, [streamUrl]);

  return (
    <div style={{ padding: '20px', background: '#000', color: '#fff', fontFamily: 'monospace' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #333', paddingBottom: '10px' }}>
        <h2>OMNI MOTHER - MoE Hardware Telemetry</h2>
        <span style={{ 
          color: status === 'LIVE' ? '#00ffcc' : '#ff3366',
          fontWeight: 'bold',
          padding: '4px 8px',
          border: `1px solid ${status === 'LIVE' ? '#00ffcc' : '#ff3366'}`,
          borderRadius: '4px'
        }}>
          {status}
        </span>
      </header>
      <div style={{ marginTop: '20px' }}>
        <canvas 
          ref={canvasRef} 
          width={800} 
          height={300} 
          style={{ width: '100%', height: '300px', border: '1px solid #222' }}
        />
      </div>
      <footer style={{ marginTop: '10px', fontSize: '12px', color: '#888' }}>
        <p>Real-time VRAM allocation bounds. Monitored strictly via Section 17 Zero-Mock policies.</p>
      </footer>
    </div>
  );
};
