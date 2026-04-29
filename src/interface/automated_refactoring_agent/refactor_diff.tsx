import React, { useState, useEffect } from 'react';

export const RefactorDiff: React.FC = () => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setStep(1);
    }, 2500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-emerald-400">AI Refactoring</h2>
        <p className="text-xs text-slate-400">Code Smell Elimination</p>
      </div>

      <div className="space-y-4">
         {/* Original Code */}
         <div className="relative">
            <div className="text-[10px] uppercase font-bold text-rose-400 mb-1">Legacy Code (Complexity: 14)</div>
            <div className={`bg-slate-950 p-3 rounded border border-rose-900/50 font-mono text-xs text-slate-400 transition-opacity duration-1000 ${step === 1 ? 'opacity-30 line-through' : ''}`}>
<pre>{`function process(d) {
  var x = 0;
  try {
     for(var i=0;i<d.length;i++){
        if(d[i] != null) x += d[i];
     }
  } catch(e) { console.log(e); }
  return x;
}`}</pre>
            </div>
         </div>

         {/* Refactored Code */}
         {step === 1 && (
            <div className="relative animate-fade-in">
               <div className="text-[10px] uppercase font-bold text-emerald-400 mb-1 flex justify-between">
                  <span>OMNI Idiomatic (Complexity: 2)</span>
                  <span className="text-emerald-500 bg-emerald-900/30 px-1 rounded">Applied</span>
               </div>
               <div className="bg-slate-950 p-3 rounded border border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.1)] font-mono text-xs text-emerald-300">
<pre>{`fn process_data(data: &[f64]) -> Result<f64, ProcessError> {
    let sum = data.iter()
        .filter(|&&val| !val.is_nan())
        .sum();
    Ok(sum)
}`}</pre>
               </div>
            </div>
         )}
      </div>
      
      {step === 0 && (
         <div className="mt-4 flex items-center justify-center gap-2 text-xs text-slate-500 animate-pulse">
            <div className="w-4 h-4 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            Analyzing AST for Monadic compliance...
         </div>
      )}
    </div>
  );
};
