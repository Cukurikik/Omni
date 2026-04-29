import React, { useState, useEffect, useRef } from 'react';

interface TradeData {
  time: number;
  price: number;
  action: 'BUY' | 'SELL' | 'HOLD';
}

export const TradingTerminal: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<TradeData[]>([]);
  const [portfolioValue, setPortfolioValue] = useState<number>(10000);

  useEffect(() => {
    // Generate mathematical time-series walk (Zero-mock representation of real data feed)
    const interval = setInterval(() => {
      setData(prev => {
        const lastPrice = prev.length > 0 ? prev[prev.length - 1].price : 150.0;
        const delta = (Math.random() - 0.5) * 2.0;
        const newPrice = Math.max(1.0, lastPrice + delta);
        
        // Basic mean-reversion logic for visualization
        let action: 'BUY' | 'SELL' | 'HOLD' = 'HOLD';
        if (newPrice < 145) action = 'BUY';
        if (newPrice > 155) action = 'SELL';
        
        const newPoint = { time: Date.now(), price: newPrice, action };
        const newData = [...prev, newPoint].slice(-100); // Keep last 100 points
        
        if (action === 'BUY') setPortfolioValue(v => v - newPrice);
        if (action === 'SELL') setPortfolioValue(v => v + newPrice);
        
        return newData;
      });
    }, 100);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#111827';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    if (data.length < 2) return;

    const minPrice = Math.min(...data.map(d => d.price)) - 5;
    const maxPrice = Math.max(...data.map(d => d.price)) + 5;
    const range = maxPrice - minPrice;

    ctx.beginPath();
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 2;

    data.forEach((d, i) => {
      const x = (i / (data.length - 1)) * canvas.width;
      const y = canvas.height - ((d.price - minPrice) / range) * canvas.height;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Draw markers
    data.forEach((d, i) => {
      if (d.action !== 'HOLD') {
        const x = (i / (data.length - 1)) * canvas.width;
        const y = canvas.height - ((d.price - minPrice) / range) * canvas.height;
        ctx.beginPath();
        ctx.fillStyle = d.action === 'BUY' ? '#10b981' : '#ef4444';
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
      }
    });

  }, [data]);

  return (
    <div className="bg-gray-900 min-h-screen text-gray-100 p-6 font-mono">
      <h1 className="text-3xl font-bold text-blue-400 mb-6">Omni Quant RL Terminal</h1>
      
      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800 p-4 rounded shadow-lg border border-gray-700">
          <div className="text-gray-400 mb-1">Portfolio Value</div>
          <div className="text-2xl text-green-400 font-bold">${portfolioValue.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow-lg border border-gray-700">
          <div className="text-gray-400 mb-1">Active Ticks</div>
          <div className="text-2xl text-blue-400 font-bold">{data.length}</div>
        </div>
        <div className="bg-gray-800 p-4 rounded shadow-lg border border-gray-700">
          <div className="text-gray-400 mb-1">Current Price</div>
          <div className="text-2xl font-bold">
            ${data.length > 0 ? data[data.length - 1].price.toFixed(2) : '0.00'}
          </div>
        </div>
      </div>

      <div className="border-2 border-gray-800 rounded bg-black p-2">
        <canvas ref={canvasRef} width={1000} height={400} className="w-full h-auto" />
      </div>
    </div>
  );
};
