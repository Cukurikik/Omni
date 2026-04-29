import React, { useState, useEffect } from 'react';

export const BondingCurve: React.FC = () => {
  const [reserveX, setReserveX] = useState(1000); // ETH
  const [reserveY, setReserveY] = useState(3000000); // USDC
  const [lastSwap, setLastSwap] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate random AMM Swaps
      const isBuyingEth = Math.random() > 0.5;
      const amount = Math.random() * 50; // Random trade size

      if (isBuyingEth) {
         // User puts in USDC, takes out ETH
         const inputY = amount * 3000;
         const outputX = (inputY * 0.997 * reserveX) / (reserveY + inputY * 0.997);
         setReserveX(prev => prev - outputX);
         setReserveY(prev => prev + inputY);
         setLastSwap(outputX);
      } else {
         // User puts in ETH, takes out USDC
         const inputX = amount;
         const outputY = (inputX * 0.997 * reserveY) / (reserveX + inputX * 0.997);
         setReserveX(prev => prev + inputX);
         setReserveY(prev => prev - outputY);
         setLastSwap(-inputX);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [reserveX, reserveY]);

  const currentPrice = reserveY / reserveX;
  const k = reserveX * reserveY;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-fuchsia-400">DeFi AMM</h2>
          <p className="text-xs text-slate-400">Constant Product (x*y=k)</p>
        </div>
        <div className="px-2 py-1 bg-fuchsia-900/30 text-fuchsia-400 text-[10px] font-mono rounded border border-fuchsia-800">
          ETH/USDC
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 mb-4 relative h-[150px] overflow-hidden">
         {/* Bonding Curve Visualization */}
         <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
            {/* The hyperbola x*y=k */}
            <path d="M 5,95 Q 20,20 95,5" fill="none" stroke="#334155" strokeWidth="2" />
            
            {/* Current Price Point */}
            <circle 
               cx={(reserveX / 2000) * 100} 
               cy={100 - (reserveY / 6000000) * 100} 
               r="4" fill="#e879f9" className="shadow-[0_0_10px_#e879f9]" 
            />
         </svg>
         <div className="absolute top-2 right-2 text-[10px] font-mono text-slate-500">
            Price: <span className="text-white">${currentPrice.toFixed(2)}</span>
         </div>
      </div>
      
      <div className="space-y-2 mb-4">
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Pool ETH (x)</span>
            <span className="text-blue-400 font-bold">{reserveX.toFixed(2)}</span>
         </div>
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Pool USDC (y)</span>
            <span className="text-emerald-400 font-bold">${reserveY.toFixed(2)}</span>
         </div>
      </div>

      <div className="text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded flex justify-between">
         <span>Constant (k): {(k/1000000).toFixed(0)}M</span>
         <span>Last Trade: <span className={lastSwap > 0 ? 'text-emerald-400' : 'text-red-400'}>{lastSwap > 0 ? '+' : ''}{lastSwap.toFixed(2)} ETH</span></span>
      </div>
    </div>
  );
};
