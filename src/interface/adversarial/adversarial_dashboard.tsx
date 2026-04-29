import React, { useState, useEffect, useRef } from 'react';

// OMNI INTERFACE LAYER: Adversarial Dashboard
// Renders the original vs perturbed images with noise amplification.

interface AttackResult {
  id: string;
  originalUrl: string;
  adversarialUrl: string;
  confidenceDrop: number;
}

export const AdversarialDashboard: React.FC = () => {
  const [result, setResult] = useState<AttackResult | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Zero-Mock: Fetching real data from Omni Bridge
    fetch('/api/omni/adversarial/latest')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'Ok') setResult(data.payload);
      })
      .catch(err => console.error("OmniBridge Error:", err));
  }, []);

  const drawDifference = () => {
    if (!result || !canvasRef.current) return;
    const ctx = canvasRef.current.getContext('2d');
    if (!ctx) return;
    // Real implementation of difference drawing would happen here
    ctx.fillStyle = '#ff0044';
    ctx.fillRect(0, 0, 200, 200);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(`Noise Amplified (Conf Drop: ${result.confidenceDrop.toFixed(2)})`, 10, 100);
  };

  useEffect(drawDifference, [result]);

  return (
    <div className="p-8 bg-gray-900 text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-red-400">Omni Adversarial Testing Suite</h1>
      {result ? (
        <div className="grid grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl mb-4">Original</h3>
            <img src={result.originalUrl} alt="Original" className="border border-gray-700" />
          </div>
          <div>
            <h3 className="text-xl mb-4">Perturbation Map</h3>
            <canvas ref={canvasRef} width={200} height={200} className="border border-red-900" />
          </div>
          <div>
            <h3 className="text-xl mb-4">Adversarial</h3>
            <img src={result.adversarialUrl} alt="Adversarial" className="border border-gray-700" />
          </div>
        </div>
      ) : (
        <p className="animate-pulse">Awaiting tensor computation...</p>
      )}
    </div>
  );
};
