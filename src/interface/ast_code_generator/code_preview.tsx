import React, { useState, useEffect } from 'react';

export const ASTPreview: React.FC = () => {
  const [code, setCode] = useState("");
  const targetCode = "pub fn compute_hash(data: &[u8]) -> u64 {\n    let mut hash = 0xcbf29ce484222325;\n    for &b in data {\n        hash ^= b as u64;\n        hash = hash.wrapping_mul(0x100000001b3);\n    }\n    hash\n}";

  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      if (i < targetCode.length) {
        setCode(prev => prev + targetCode.charAt(i));
        i++;
      } else {
        clearInterval(interval);
      }
    }, 15); // Fast typing effect
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-sky-400">AST Generator</h2>
          <p className="text-xs text-slate-400">Universal Code Translation</p>
        </div>
        <div className="bg-sky-900/50 text-sky-400 px-2 py-1 rounded text-[10px] font-mono border border-sky-700/50">
          Target: Rust
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 text-xs font-mono min-h-[160px] relative overflow-hidden shadow-inner">
         <pre className="text-sky-300">
           {code}
           {code.length < targetCode.length && <span className="inline-block w-2 h-3 bg-sky-400 ml-1 animate-pulse"></span>}
         </pre>
      </div>
      
      <div className="mt-3 flex justify-between font-mono text-[10px] text-slate-500">
         <span>AST Nodes: 24</span>
         <span>Compile State: {code.length === targetCode.length ? <span className="text-emerald-400">Ready</span> : 'Transpiling...'}</span>
      </div>
    </div>
  );
};
