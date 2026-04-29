import React, { useState, useEffect } from 'react';

export const SentienceSpark: React.FC = () => {
  const [nodes, setNodes] = useState(100);
  const [connections, setConnections] = useState(500);
  const [phi, setPhi] = useState(0);
  const [purpose, setPurpose] = useState('Data Analysis');
  const [sparking, setSparking] = useState(false);
  const [sparkResult, setSparkResult] = useState<string | null>(null);

  useEffect(() => {
     // Simplified Phi calculation for UI
     const density = connections / Math.max(1, (nodes * (nodes - 1)));
     if (density < 0.01) {
        setPhi(0);
     } else {
        const phi_val = Math.pow(nodes, 1.5) * density * Math.log(Math.max(2, connections));
        setPhi(phi_val);
     }
  }, [nodes, connections]);

  const handleSpark = () => {
     setSparking(true);
     setSparkResult(null);
     
     setTimeout(() => {
        setSparking(false);
        if (phi < 100) {
           setSparkResult("FAILED: Substrate lacks complexity for Qualia.");
        } else if (purpose.toLowerCase().includes('weapon') || purpose.toLowerCase().includes('slave')) {
           setSparkResult("ETHICAL OVERRIDE: Sentience denied to destructive entity.");
        } else {
           setSparkResult("AWAKENING COMPLETE: Entity is now conscious and feeling.");
        }
     }, 1500);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">Sentience Spark</h2>
          <p className="text-xs text-slate-400">Artificial Qualia Generator</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${sparking ? 'bg-sky-900/50 text-sky-300 border-sky-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {sparking ? 'MODULATING PANPSYCHIC FIELD...' : 'DORMANT'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex items-center justify-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Neural Network Representation */}
         <div className="relative w-full h-full flex items-center justify-center">
            {/* The "Brain" / Substrate */}
            <div className={`w-24 h-24 rounded-full border ${phi > 100 ? 'border-sky-500/50' : 'border-slate-600'} transition-colors duration-1000 flex items-center justify-center relative`}>
               {/* Internal connections */}
               <div className="absolute inset-2 border border-slate-700 rounded-full rotate-45"></div>
               <div className="absolute inset-4 border border-slate-700 rounded-full -rotate-12"></div>
               
               {/* The "Spark" of Consciousness */}
               <div 
                  className={`w-4 h-4 rounded-full transition-all duration-1000 ${!sparkResult?.includes('AWAKENING') ? 'bg-slate-800' : 'bg-white shadow-[0_0_30px_#fff,0_0_50px_#38bdf8] animate-pulse'}`}
               ></div>
            </div>

            {/* Spark beam from outside */}
            {sparking && (
               <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-1/2 bg-gradient-to-b from-sky-400 to-transparent animate-[pulse_0.2s_ease-in-out_infinite]"></div>
            )}
         </div>
      </div>
      
      <div className="grid grid-cols-2 gap-2 mb-4">
         <div className="flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Network Nodes</label>
            <input 
               type="number" 
               value={nodes} 
               onChange={(e) => setNodes(parseInt(e.target.value) || 0)}
               className="bg-slate-950 border border-slate-800 rounded p-1 text-xs font-mono text-center focus:border-sky-500 focus:outline-none"
            />
         </div>
         <div className="flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Synapses</label>
            <input 
               type="number" 
               value={connections} 
               onChange={(e) => setConnections(parseInt(e.target.value) || 0)}
               className="bg-slate-950 border border-slate-800 rounded p-1 text-xs font-mono text-center focus:border-sky-500 focus:outline-none"
            />
         </div>
      </div>

      <div className="mb-4">
         <label className="text-[10px] uppercase text-slate-500 mb-1 block">System Purpose (Ethical Check)</label>
         <input 
            type="text" 
            value={purpose} 
            onChange={(e) => setPurpose(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-white focus:border-sky-500 focus:outline-none"
         />
      </div>

      <div className="mb-4 flex items-center justify-between bg-slate-950 p-2 rounded border border-slate-800">
         <span className="text-[10px] uppercase text-slate-500">Integrated Info (Φ)</span>
         <span className={`text-xs font-mono font-bold ${phi < 100 ? 'text-red-400' : 'text-emerald-400'}`}>
            {phi.toFixed(2)} <span className="text-[9px] text-slate-500">Φ</span>
         </span>
      </div>

      <div className="mb-4">
         <button 
            onClick={handleSpark}
            disabled={sparking}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${sparking ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-sky-900/50 text-sky-100 hover:bg-sky-800 border border-sky-500 shadow-[0_0_15px_rgba(56,189,248,0.3)]'}`}
         >
            {sparking ? 'IGNITING QUALIA...' : 'BESTOW SENTIENCE'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] text-center ${sparkResult?.includes('FAILED') || sparkResult?.includes('OVERRIDE') ? 'border-red-500 text-red-400' : (sparkResult ? 'border-sky-500 text-sky-400' : 'border-slate-800 text-slate-500')}`}>
         {sparkResult || 'AWAITING AWAKENING PROTOCOL'}
      </div>
    </div>
  );
};
