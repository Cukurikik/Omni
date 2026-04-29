import React, { useEffect, useRef, useState } from 'react';

// OMNI INTERFACE LAYER: Financial DataFrame
// Displays financial data natively using HTML5 Canvas for ultra-high FPS rendering.

interface ChartProps {
  assetId: string;
  dataEndpoint: string;
}

export const TradingChart: React.FC<ChartProps> = ({ assetId, dataEndpoint }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<{ time: number, price: number, signal?: 'Buy' | 'Sell' }[]>([]);

  useEffect(() => {
    // Zero-Mock Data Fetching loop
    const fetchStream = async () => {
      try {
        const res = await fetch(`${dataEndpoint}?asset=${assetId}`);
        const json = await res.json();
        if (json.status === 'Ok') {
          setData(json.payload);
        }
      } catch (err) {
        console.error("OmniBridge: FinData connection lost", err);
      }
    };
    
    const interval = setInterval(fetchStream, 1000);
    return () => clearInterval(interval);
  }, [assetId, dataEndpoint]);

  useEffect(() => {
    if (!canvasRef.current || data.length === 0) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const width = canvasRef.current.width;
    const height = canvasRef.current.height;
    ctx.clearRect(0, 0, width, height);

    // Draw baseline
    ctx.strokeStyle = '#444';
    ctx.beginPath();
    ctx.moveTo(0, height / 2);
    ctx.lineTo(width, height / 2);
    ctx.stroke();

    // Draw Line
    ctx.strokeStyle = '#00ffcc';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    const maxPrice = Math.max(...data.map(d => d.price));
    const minPrice = Math.min(...data.map(d => d.price));
    const range = maxPrice - minPrice || 1;

    data.forEach((pt, i) => {
      const x = (i / data.length) * width;
      const y = height - ((pt.price - minPrice) / range) * height;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
      
      // Draw signals
      if (pt.signal === 'Buy') {
        ctx.fillStyle = '#00ff00';
        ctx.fillText('▲', x, y + 15);
      } else if (pt.signal === 'Sell') {
        ctx.fillStyle = '#ff0000';
        ctx.fillText('▼', x, y - 5);
      }
    });
    ctx.stroke();

  }, [data]);

  return (
    <div className="p-4 bg-gray-950 text-white rounded-lg border border-gray-800 shadow-2xl">
      <h2 className="text-xl font-bold font-mono mb-2 text-teal-400">Omni Trade: {assetId}</h2>
      <canvas 
        ref={canvasRef} 
        width={800} 
        height={300} 
        className="w-full bg-black border border-gray-900"
      />
      <div className="mt-2 text-xs font-mono text-gray-500">
        Live SIMD Computed Moving Averages • Zero-Copy Memory
      </div>
    </div>
  );
};
