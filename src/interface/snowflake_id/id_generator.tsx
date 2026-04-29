import React, { useState, useEffect } from 'react';

export const IdGenerator: React.FC = () => {
  const [ids, setIds] = useState<{id: string, time: string}[]>([]);
  const machineId = 42;

  useEffect(() => {
    let seq = 0;
    const interval = setInterval(() => {
      // Deterministic Snowflake ID Generation Math simulation in JS
      const now = Date.now();
      seq = (seq + 1) % 4096;
      
      // JS numbers are double precision floats, safe integer limit is 53 bits.
      // Full 64-bit snowflake requires BigInt
      const timestampPart = BigInt(now - 1600000000000) << 22n;
      const machinePart = BigInt(machineId) << 12n;
      const seqPart = BigInt(seq);
      
      const snowflake = (timestampPart | machinePart | seqPart).toString();
      
      const timeStr = new Date(now).toISOString().split('T')[1].slice(0, 12);

      setIds(prev => [{id: snowflake, time: timeStr}, ...prev].slice(0, 6));
    }, 150);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-3">
        <div>
          <h2 className="text-xl font-bold text-emerald-400">Snowflake IDs</h2>
          <p className="text-xs text-slate-400">Distributed 64-bit Generation</p>
        </div>
        <div className="text-[10px] font-mono text-slate-400 bg-slate-800 px-2 py-1 rounded">
          Node {machineId}
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {ids.map((item, i) => (
          <div key={item.id} className="bg-slate-800 px-3 py-2 rounded border border-slate-700 flex justify-between items-center font-mono">
            <div className="text-sm font-bold text-slate-300 tracking-wider">
              {item.id}
            </div>
            <div className="text-[10px] text-emerald-500">
              {item.time}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 flex gap-1 h-2 rounded overflow-hidden">
         <div className="w-[64%] bg-slate-600" title="41-bit Timestamp"></div>
         <div className="w-[16%] bg-emerald-600" title="10-bit Node ID"></div>
         <div className="w-[20%] bg-sky-600" title="12-bit Sequence"></div>
      </div>
      <div className="flex justify-between text-[8px] text-slate-500 mt-1 uppercase font-bold tracking-widest px-1">
        <span>Time</span>
        <span>Node</span>
        <span>Seq</span>
      </div>
    </div>
  );
};
