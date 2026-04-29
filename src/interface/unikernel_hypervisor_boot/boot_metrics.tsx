import React, { useState, useEffect } from 'react';

export const BootMetrics: React.FC = () => {
  const [bootLog, setBootLog] = useState<{time: number, msg: string}[]>([]);
  const [isBooted, setIsBooted] = useState(false);

  useEffect(() => {
    // Simulate a 5-millisecond Unikernel boot sequence
    const sequence = [
      { t: 0.1, m: "KVM_CREATE_VM... OK" },
      { t: 0.5, m: "Allocating 32MB HugePages... OK" },
      { t: 0.8, m: "Loading ELF binary to 0x100000... OK" },
      { t: 1.2, m: "Setting CR3 (Page Tables)... OK" },
      { t: 2.0, m: "Verifying Secure Boot Attestation... OK" },
      { t: 2.5, m: "KVM_SET_REGS (RIP=0x100000)... OK" },
      { t: 3.0, m: "KVM_RUN... Yielding to Guest" },
      { t: 4.8, m: "Guest initialized TCP stack." },
      { t: 5.2, m: "Listening on :8080. Ready." }
    ];

    let currentStep = 0;
    const interval = setInterval(() => {
       if (currentStep < sequence.length) {
          setBootLog(prev => [...prev, { time: sequence[currentStep].t, msg: sequence[currentStep].m }]);
          if (currentStep === sequence.length - 1) setIsBooted(true);
          currentStep++;
       } else {
          clearInterval(interval);
       }
    }, 150); // Slowed down for UI visibility, actual is 5ms

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-orange-500">Unikernel Hypervisor</h2>
          <p className="text-xs text-slate-400">Bare-Metal KVM MicroVM</p>
        </div>
        <div className={`px-2 py-1 rounded text-[10px] font-mono border ${isBooted ? 'bg-emerald-900/30 text-emerald-400 border-emerald-800' : 'bg-orange-900/50 text-orange-400 border-orange-800 animate-pulse'}`}>
          {isBooted ? 'RUNNING' : 'BOOTING'}
        </div>
      </div>

      <div className="bg-black p-4 rounded border border-slate-800 mb-4 h-[200px] overflow-y-auto font-mono text-[10px] space-y-1">
         {bootLog.map((log, i) => (
            <div key={i} className="flex space-x-2">
               <span className="text-slate-500">[{log.time.toFixed(1)}ms]</span>
               <span className={log.msg.includes("Ready") ? "text-emerald-400 font-bold" : "text-slate-300"}>{log.msg}</span>
            </div>
         ))}
         {!isBooted && (
            <div className="flex space-x-2 mt-2">
               <span className="text-slate-500">[ _._ms]</span>
               <span className="text-orange-400 animate-pulse">_</span>
            </div>
         )}
      </div>
      
      <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-slate-400 bg-slate-800 p-2 rounded">
         <span>Image Size: <span className="text-white">4.2 MB</span></span>
         <span>Memory: <span className="text-emerald-400">32 MB</span></span>
         <span className="col-span-2">OS Context Switches: <span className="text-white font-bold">0 (Bypassed)</span></span>
      </div>
    </div>
  );
};
