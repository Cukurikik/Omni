import React, { useState, useEffect } from 'react';

export const SpacecraftDashboard: React.FC = () => {
  const [voltage, setVoltage] = useState(28.4);
  const [rxBytes, setRxBytes] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate telemetry updates
      setVoltage(prev => {
         const next = prev + (Math.random() * 0.4 - 0.2);
         return Math.max(20, Math.min(32, next));
      });
      setRxBytes(prev => prev + 1024 + Math.random() * 512);
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const isFault = voltage < 22.0;

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Spacecraft Telemetry</h2>
          <p className="text-xs text-slate-400">CCSDS Frame Sync</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold ${isFault ? 'bg-red-900/50 text-red-400 border border-red-800 animate-pulse' : 'bg-emerald-900/30 text-emerald-400 border border-emerald-800'}`}>
          {isFault ? 'SAFE MODE' : 'NOMINAL'}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
         <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center">
            <div className="text-[10px] uppercase text-slate-500 mb-1">Bus Voltage</div>
            <div className={`text-2xl font-mono font-bold ${isFault ? 'text-red-400' : 'text-sky-400'}`}>
               {voltage.toFixed(2)}V
            </div>
         </div>
         
         <div className="bg-slate-950 p-4 rounded border border-slate-800 text-center">
            <div className="text-[10px] uppercase text-slate-500 mb-1">X-Band Downlink</div>
            <div className="text-2xl font-mono font-bold text-emerald-400">
               Lock <span className="text-xs">OK</span>
            </div>
         </div>
      </div>
      
      <div className="space-y-2">
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">Bytes Received</span>
            <span className="text-white font-bold">{(rxBytes / 1024).toFixed(1)} KB</span>
         </div>
         <div className="w-full bg-slate-800 p-2 rounded flex justify-between items-center text-xs font-mono">
            <span className="text-slate-400">SDR Demodulator</span>
            <span className="text-emerald-400 font-bold">BPSK Locked</span>
         </div>
         <div className="w-full bg-slate-800 p-2 rounded flex flex-col justify-center text-[8px] font-mono">
            <span className="text-slate-500 mb-1">Raw Hex Stream (Simulated):</span>
            <span className="text-sky-300 break-all leading-tight opacity-70">
               1A CF FC 1D 08 00 00 00 1A CF FC 1D 08 00 00 00 1A CF FC 1D
            </span>
         </div>
      </div>
    </div>
  );
};
