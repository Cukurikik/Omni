import React, { useEffect, useRef, useState } from 'react';

// OMNI INTERFACE LAYER: Forecast Chart
// Render time series history, kalman filtered line, and future predictions.

interface Point { x: number; y: number }

interface TimeSeriesData {
  history: Point[];
  filtered: Point[];
  forecast: Point[];
}

export const ForecastChart: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [data, setData] = useState<TimeSeriesData | null>(null);

  useEffect(() => {
    // Zero-Mock fetch
    fetch('/api/omni/timeseries/telemetry')
      .then(res => res.json())
      .then(json => {
        if (json.status === 'Ok') setData(json.payload);
      })
      .catch(err => console.error("OmniBridge Error", err));
  }, []);

  useEffect(() => {
    if (!canvasRef.current || !data) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;

    const w = canvasRef.current.width;
    const h = canvasRef.current.height;
    ctx.clearRect(0, 0, w, h);

    // Normalize coordinates
    const allPts = [...data.history, ...data.forecast];
    const maxX = Math.max(...allPts.map(p => p.x));
    const minX = Math.min(...allPts.map(p => p.x));
    const maxY = Math.max(...allPts.map(p => p.y));
    const minY = Math.min(...allPts.map(p => p.y));
    
    const scaleX = (x: number) => ((x - minX) / (maxX - minX)) * w;
    const scaleY = (y: number) => h - ((y - minY) / (maxY - minY)) * h;

    const drawLine = (pts: Point[], color: string, dash: number[] = []) => {
      if (pts.length === 0) return;
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.setLineDash(dash);
      ctx.moveTo(scaleX(pts[0].x), scaleY(pts[0].y));
      for (let i = 1; i < pts.length; i++) {
        ctx.lineTo(scaleX(pts[i].x), scaleY(pts[i].y));
      }
      ctx.stroke();
      ctx.setLineDash([]);
    };

    drawLine(data.history, 'rgba(100, 100, 100, 0.5)'); // Raw
    drawLine(data.filtered, '#00ffff'); // Kalman Filtered
    
    // Connect filtered to forecast
    if (data.filtered.length > 0 && data.forecast.length > 0) {
      const lastFilt = data.filtered[data.filtered.length - 1];
      const firstFore = data.forecast[0];
      ctx.beginPath();
      ctx.strokeStyle = '#ff00ff';
      ctx.setLineDash([5, 5]);
      ctx.moveTo(scaleX(lastFilt.x), scaleY(lastFilt.y));
      ctx.lineTo(scaleX(firstFore.x), scaleY(firstFore.y));
      ctx.stroke();
      ctx.setLineDash([]);
    }

    drawLine(data.forecast, '#ff00ff', [5, 5]); // Forecast

  }, [data]);

  return (
    <div className="p-6 bg-slate-900 rounded-xl shadow-2xl font-sans text-white border border-slate-700">
      <h2 className="text-xl font-bold mb-4 text-cyan-400">Omni Stream Telemetry & ARIMA Forecast</h2>
      <canvas 
        ref={canvasRef} 
        width={800} 
        height={300} 
        className="w-full bg-slate-950 rounded border border-slate-800"
      />
      <div className="mt-4 flex gap-6 text-sm text-slate-400 font-mono">
        <span className="flex items-center gap-2"><div className="w-4 h-1 bg-slate-500"></div> Raw Noise</span>
        <span className="flex items-center gap-2"><div className="w-4 h-1 bg-cyan-400"></div> C++ Kalman Filter</span>
        <span className="flex items-center gap-2"><div className="w-4 h-1 border-b-2 border-dashed border-fuchsia-500"></div> Py ARIMA</span>
      </div>
    </div>
  );
};
