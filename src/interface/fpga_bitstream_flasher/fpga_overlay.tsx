import React, { useState, useEffect } from 'react';

export const FpgaOverlay: React.FC = () => {
  const [flashingRegion, setFlashingRegion] = useState<number | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate Partial Reconfiguration of random FPGA regions
      setFlashingRegion(Math.floor(Math.random() * 4));
      setTimeout(() => setFlashingRegion(null), 800);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">FPGA Array</h2>
          <p className="text-xs text-slate-400">Dynamic Bitstream Routing</p>
        </div>
        <div className="px-2 py-1 bg-slate-800 text-orange-400 text-[10px] font-mono rounded border border-orange-900/50">
          PCIe Gen4 x16
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 relative h-[180px] mb-4">
         {/* FPGA Grid / LUTs Simulation */}
         <div className="absolute inset-0 grid grid-cols-2 grid-rows-2 p-2 gap-2">
            
            {/* Region 0: Static Network MAC */}
            <div className="border border-slate-700 bg-slate-900 rounded p-2 flex flex-col justify-between">
               <span className="text-[8px] text-slate-500 uppercase">Static Region (Eth MAC)</span>
               <div className="w-full h-1 bg-slate-700"></div>
            </div>
            
            {/* Region 1: Dynamic PR 1 */}
            <div className={`border rounded p-2 flex flex-col justify-between transition-colors duration-300 ${flashingRegion === 1 ? 'border-orange-500 bg-orange-900/30' : 'border-indigo-800 bg-indigo-900/20'}`}>
               <div className="flex justify-between items-center">
                  <span className="text-[8px] text-slate-500 uppercase">PR_1 (Tensor Core)</span>
                  {flashingRegion === 1 && <span className="text-[8px] text-orange-400 animate-pulse">FLASHING</span>}
               </div>
               <div className="grid grid-cols-4 gap-0.5 mt-2">
                  {Array.from({length:16}).map((_, i) => (
                    <div key={i} className={`h-1 ${flashingRegion === 1 ? 'bg-orange-500' : 'bg-indigo-500'}`}></div>
                  ))}
               </div>
            </div>
            
            {/* Region 2: Dynamic PR 2 */}
            <div className={`border rounded p-2 flex flex-col justify-between transition-colors duration-300 ${flashingRegion === 2 ? 'border-orange-500 bg-orange-900/30' : 'border-emerald-800 bg-emerald-900/20'}`}>
               <div className="flex justify-between items-center">
                  <span className="text-[8px] text-slate-500 uppercase">PR_2 (Activation)</span>
                  {flashingRegion === 2 && <span className="text-[8px] text-orange-400 animate-pulse">FLASHING</span>}
               </div>
               <div className="grid grid-cols-4 gap-0.5 mt-2">
                  {Array.from({length:16}).map((_, i) => (
                    <div key={i} className={`h-1 ${flashingRegion === 2 ? 'bg-orange-500' : 'bg-emerald-500'}`}></div>
                  ))}
               </div>
            </div>
            
            {/* Region 3: Static PCIe Controller */}
            <div className="border border-slate-700 bg-slate-900 rounded p-2 flex flex-col justify-between">
               <span className="text-[8px] text-slate-500 uppercase">Static Region (PCIe DMA)</span>
               <div className="flex gap-1 mt-2">
                  <div className="w-2 h-2 bg-slate-600 rounded-full animate-ping"></div>
                  <div className="w-2 h-2 bg-slate-600 rounded-full"></div>
                  <div className="w-2 h-2 bg-slate-600 rounded-full animate-ping delay-75"></div>
               </div>
            </div>

         </div>
      </div>

      <div className="flex justify-between text-[10px] font-mono text-slate-400">
         <span>Total LUTs: 1.2M</span>
         <span>DSP Slices: 4,096</span>
         <span>BRAM: 120Mb</span>
      </div>
    </div>
  );
};
