import React, { useState, useEffect } from 'react';

export const Level2Book: React.FC = () => {
  const [bids, setBids] = useState<{price: number, size: number}[]>([]);
  const [asks, setAsks] = useState<{price: number, size: number}[]>([]);
  const [lastPrice, setLastPrice] = useState(42069.00);

  useEffect(() => {
    // Generate initial order book
    const initialBids = [];
    const initialAsks = [];
    let currentBid = 42068.50;
    let currentAsk = 42069.50;

    for (let i = 0; i < 10; i++) {
       initialBids.push({ price: currentBid - (i * 0.5), size: Math.floor(Math.random() * 50) + 1 });
       initialAsks.push({ price: currentAsk + (i * 0.5), size: Math.floor(Math.random() * 50) + 1 });
    }
    setBids(initialBids);
    setAsks(initialAsks);

    const interval = setInterval(() => {
      // Simulate HFT Market Making and Taker orders eating into the book
      const isBuy = Math.random() > 0.5;
      if (isBuy) {
         setAsks(prev => {
            const next = [...prev];
            next[0].size -= Math.floor(Math.random() * 5);
            if (next[0].size <= 0) {
               setLastPrice(next[0].price);
               next.shift();
               next.push({ price: next[next.length-1].price + 0.5, size: Math.floor(Math.random() * 50) + 10 });
            }
            return next;
         });
      } else {
         setBids(prev => {
            const next = [...prev];
            next[0].size -= Math.floor(Math.random() * 5);
            if (next[0].size <= 0) {
               setLastPrice(next[0].price);
               next.shift();
               next.push({ price: next[next.length-1].price - 0.5, size: Math.floor(Math.random() * 50) + 10 });
            }
            return next;
         });
      }
    }, 100); // 10 trades per second UI update

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">HFT Matching Engine</h2>
          <p className="text-xs text-slate-400">Level 2 Order Book (OMNI/USD)</p>
        </div>
        <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse"></div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 font-mono text-xs">
         {/* Asks (Sells) - Red */}
         <div className="flex flex-col-reverse space-y-reverse space-y-1 mb-2 border-b border-slate-800 pb-2">
            {asks.slice(0, 5).reverse().map((ask, i) => (
               <div key={`ask-${i}`} className="flex justify-between text-red-400 relative">
                  <div className="absolute top-0 right-0 h-full bg-red-900/30 -z-10" style={{ width: `${(ask.size / 60) * 100}%` }}></div>
                  <span>{ask.price.toFixed(2)}</span>
                  <span>{ask.size}</span>
               </div>
            ))}
         </div>

         {/* Spread / Last Price */}
         <div className="flex justify-between items-center py-2 text-lg font-bold text-white">
            <span>{lastPrice.toFixed(2)}</span>
            <span className="text-xs text-slate-500 font-normal">Spread: {(asks[0].price - bids[0].price).toFixed(2)}</span>
         </div>

         {/* Bids (Buys) - Green */}
         <div className="flex flex-col space-y-1 mt-2 border-t border-slate-800 pt-2">
            {bids.slice(0, 5).map((bid, i) => (
               <div key={`bid-${i}`} className="flex justify-between text-emerald-400 relative">
                  <div className="absolute top-0 right-0 h-full bg-emerald-900/30 -z-10" style={{ width: `${(bid.size / 60) * 100}%` }}></div>
                  <span>{bid.price.toFixed(2)}</span>
                  <span>{bid.size}</span>
               </div>
            ))}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Latency: <span className="text-emerald-400">12 ns (FPGA)</span></span>
         <span>Engine: <span className="text-white">Price/Time FIFO</span></span>
      </div>
    </div>
  );
};
