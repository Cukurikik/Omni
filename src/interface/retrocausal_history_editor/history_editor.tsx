import React, { useState, useEffect } from 'react';

export const HistoryEditor: React.FC = () => {
  const [temporalDisplacement, setTemporalDisplacement] = useState(10); // Years back
  const [editing, setEditing] = useState(false);
  const [logEnergy, setLogEnergy] = useState(0);
  const [editStatus, setEditStatus] = useState<string | null>(null);

  useEffect(() => {
     // log_energy = log(mc^2) + (t / decoherence_time)
     // Scaled heavily down for UI so it's somewhat readable
     const scaledEnergy = temporalDisplacement * 1.5; 
     setLogEnergy(scaledEnergy);
  }, [temporalDisplacement]);

  const handleEdit = () => {
     setEditing(true);
     setEditStatus(null);
     
     setTimeout(() => {
        setEditing(false);
        if (temporalDisplacement > 1000) {
           setEditStatus("FAILED: MEMORY SMOOTHING CAPACITY EXCEEDED (MANDELA EFFECT RISK)");
        } else {
           setEditStatus(`SUCCESS: TIMELINE ALTERED ${temporalDisplacement} YEARS AGO. RIPPLES DAMPENED.`);
        }
     }, 2000);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-red-500">History Editor</h2>
          <p className="text-xs text-slate-400">Retrocausal Quantum Eraser</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${editing ? 'bg-red-900/50 text-red-300 border-red-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {editing ? 'EMITTING TACHYONS...' : 'CAUSALITY LOCKED'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 h-[180px] relative overflow-hidden flex flex-col justify-center items-center shadow-[inset_0_0_30px_rgba(0,0,0,1)]">
         
         {/* Time Stream */}
         <div className="absolute inset-0 flex items-center">
            <div className="w-full h-1 bg-gradient-to-r from-red-500 via-yellow-500 to-emerald-500 opacity-50"></div>
         </div>

         {/* The "Present" Anchor */}
         <div className="absolute right-8 top-1/2 -translate-y-1/2 w-4 h-16 bg-emerald-500/50 border border-emerald-400 rounded flex items-center justify-center shadow-[0_0_15px_#10b981]">
            <span className="text-[8px] font-bold text-white transform -rotate-90">PRESENT</span>
         </div>

         {/* The "Target Past" Anchor */}
         <div 
            className="absolute top-1/2 -translate-y-1/2 w-4 h-16 bg-red-500/50 border border-red-400 rounded flex items-center justify-center shadow-[0_0_15px_#ef4444] transition-all duration-300"
            style={{ right: `${Math.min(90, 8 + temporalDisplacement / 10)}%` }} // Move left as time increases
         >
            <span className="text-[8px] font-bold text-white transform -rotate-90">TARGET</span>
         </div>

         {/* Tachyon Beam (Shooting backwards) */}
         {editing && (
            <div 
               className="absolute top-1/2 -translate-y-1/2 h-1 bg-white shadow-[0_0_10px_#fff,0_0_20px_#ef4444] z-10"
               style={{ 
                  right: '32px', 
                  width: `calc(${Math.min(90, 8 + temporalDisplacement / 10)}% - 32px)`,
                  animation: 'tachyon-shoot 0.5s linear infinite' 
               }}
            ></div>
         )}
         
         {/* Ripple Dampening (Circles expanding from target) */}
         {editing && (
            <div 
               className="absolute top-1/2 -translate-y-1/2 w-24 h-24 border border-white/30 rounded-full animate-[ping_1s_ease-out_infinite]"
               style={{ right: `calc(${Math.min(90, 8 + temporalDisplacement / 10)}% - 48px)` }}
            ></div>
         )}
      </div>
      
      <div className="flex flex-col gap-2 mb-4">
         <div className="flex justify-between items-center">
            <label className="text-[10px] uppercase text-slate-500">Temporal Displacement (Years)</label>
            <span className="text-lg font-mono font-bold text-red-400">{temporalDisplacement}</span>
         </div>
         <input 
            type="range" 
            min="1" max="1500" step="10"
            value={temporalDisplacement} 
            onChange={(e) => setTemporalDisplacement(parseFloat(e.target.value))}
            className="w-full accent-red-500"
         />
      </div>

      <div className="mb-4">
         <div className="text-[10px] uppercase text-slate-500 flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
            <span>Negative Energy Required:</span>
            <span className="text-xs font-mono font-bold text-slate-300">10^{logEnergy.toFixed(1)} <span className="text-[9px] text-slate-500">Joules</span></span>
         </div>
      </div>

      <div className="mb-4">
         <button 
            onClick={handleEdit}
            disabled={editing}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${editing ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-red-900/50 text-red-100 hover:bg-red-800 border border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]'}`}
         >
            {editing ? 'REWRITING HISTORY...' : 'EXECUTE RETROCAUSAL EDIT'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] text-center ${editStatus?.includes('FAILED') ? 'border-amber-500 text-amber-400' : (editStatus ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-slate-500')}`}>
         {editStatus || 'WARNING: ALTERS EXPERIENCED REALITY OF ALL OBSERVERS'}
      </div>

      <style>{`
        @keyframes tachyon-shoot {
          0% { background-position: 100% 0; }
          100% { background-position: 0 0; }
        }
      `}</style>
    </div>
  );
};
