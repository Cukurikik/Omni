import React, { useState, useEffect } from 'react';

export const RealityPatchNotes: React.FC = () => {
  const [constantName, setConstantName] = useState('Speed of Light (c)');
  const [currentValue, setCurrentValue] = useState(299792458);
  const [newValue, setNewValue] = useState(299792458);
  const [stability, setStability] = useState(1.0);
  const [deploying, setDeploying] = useState(false);
  const [deployStatus, setDeployStatus] = useState<string | null>(null);

  useEffect(() => {
    const ratio = Math.abs(newValue - currentValue) / currentValue;
    const stab = Math.exp(-5.0 * ratio);
    setStability(stab);
  }, [newValue, currentValue]);

  const handleDeploy = () => {
     setDeploying(true);
     setDeployStatus(null);
     
     setTimeout(() => {
        setDeploying(false);
        if (stability < 0.95) {
           setDeployStatus("FATAL: VACUUM DECAY DETECTED. ROLLBACK INITIATED.");
        } else {
           setDeployStatus("SUCCESS: REALITY PATCH v1.0.4 APPLIED. NO OBSERVER DOWNTIME.");
           setCurrentValue(newValue);
        }
     }, 1500);
  };

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-teal-400">Physics Patch UI</h2>
          <p className="text-xs text-slate-400">Fundamental Constant Rewriter</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-bold border ${deploying ? 'bg-teal-900/50 text-teal-300 border-teal-500 animate-pulse' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
          {deploying ? 'RECOMPILING VACUUM...' : 'IDLE'}
        </div>
      </div>

      <div className="bg-[#050510] p-4 rounded border border-slate-800 mb-4 flex flex-col gap-3">
         <div className="flex flex-col">
            <label className="text-[10px] uppercase text-slate-500 mb-1">Target Constant</label>
            <select 
               className="bg-slate-950 border border-slate-800 rounded p-1 text-sm font-mono focus:outline-none focus:border-teal-500"
               value={constantName}
               onChange={(e) => {
                  setConstantName(e.target.value);
                  if (e.target.value === 'Speed of Light (c)') { setCurrentValue(299792458); setNewValue(299792458); }
                  if (e.target.value === 'Planck (h)') { setCurrentValue(6.626); setNewValue(6.626); }
                  if (e.target.value === 'Fine Structure (α)') { setCurrentValue(0.007297); setNewValue(0.007297); }
               }}
            >
               <option>Speed of Light (c)</option>
               <option>Planck (h)</option>
               <option>Fine Structure (α)</option>
            </select>
         </div>

         <div className="flex gap-2">
            <div className="flex-1 flex flex-col">
               <label className="text-[10px] uppercase text-slate-500 mb-1">Current Value</label>
               <input type="text" readOnly value={currentValue} className="bg-slate-900 border border-slate-800 rounded p-1 text-sm font-mono text-slate-400" />
            </div>
            <div className="flex-1 flex flex-col">
               <label className="text-[10px] uppercase text-slate-500 mb-1 text-teal-400">New Value</label>
               <input 
                  type="number" 
                  step={constantName === 'Speed of Light (c)' ? 100 : 0.0001}
                  value={newValue} 
                  onChange={(e) => setNewValue(parseFloat(e.target.value))}
                  className="bg-slate-950 border border-teal-800 rounded p-1 text-sm font-mono text-white focus:outline-none focus:border-teal-400" 
               />
            </div>
         </div>

         <div className="mt-2">
            <div className="flex justify-between items-center mb-1">
               <span className="text-[10px] uppercase text-slate-500">Stability Index</span>
               <span className={`text-[10px] font-mono font-bold ${stability < 0.95 ? 'text-red-400' : 'text-emerald-400'}`}>{(stability * 100).toFixed(2)}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded overflow-hidden">
               <div className={`h-full ${stability < 0.95 ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-emerald-500'}`} style={{ width: `${stability * 100}%` }}></div>
            </div>
         </div>
      </div>
      
      <div className="mb-4">
         <button 
            onClick={handleDeploy}
            disabled={deploying || newValue === currentValue}
            className={`w-full py-2 rounded text-xs font-bold font-mono tracking-widest transition-all ${deploying || newValue === currentValue ? 'bg-slate-800 text-slate-600 border border-slate-700 cursor-not-allowed' : 'bg-teal-900/50 text-teal-100 hover:bg-teal-800 border border-teal-500 shadow-[0_0_15px_rgba(20,184,166,0.3)]'}`}
         >
            {deploying ? 'BROADCASTING UPDATE...' : 'DEPLOY REALITY PATCH'}
         </button>
      </div>

      <div className={`w-full bg-slate-950 rounded border p-2 text-[9px] font-mono tracking-wider flex items-center justify-center min-h-[40px] ${deployStatus?.includes('FATAL') ? 'border-red-500 text-red-400' : (deployStatus ? 'border-emerald-500 text-emerald-400' : 'border-slate-800 text-slate-500')}`}>
         {deployStatus || 'AWAITING PHYSICS MODIFICATION'}
      </div>
    </div>
  );
};
