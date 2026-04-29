import React, { useState, useEffect } from 'react';

export const EquationExplorer: React.FC = () => {
  const [generation, setGeneration] = useState(1);
  const [bestEq, setBestEq] = useState("x");
  const [fitness, setFitness] = useState(0.1);

  useEffect(() => {
    let t = 0;
    const interval = setInterval(() => {
      t++;
      
      // Deterministic evolutionary progress simulation
      setGeneration(prev => prev + 1);
      
      const equations = [
        "x", "2*x", "sin(x)", "sin(x) + 0.5*x", 
        "x^2 - sin(x)", "9.81 * x^2 / 2", "E = m*c^2"
      ];
      
      const phase = Math.floor(t / 10);
      if (phase < equations.length) {
        setBestEq(equations[phase]);
        // Fitness approaches 1.0 deterministically
        setFitness(prev => Math.min(0.999, prev + (1.0 - prev) * 0.15));
      }

    }, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 shadow-2xl max-w-lg mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-800 pb-4 flex justify-between items-end">
        <div>
          <h2 className="text-xl font-bold text-pink-400">PhySO Optimizer</h2>
          <p className="text-xs text-slate-500">Physical Symbolic Regression</p>
        </div>
        <div className="text-sm font-mono text-pink-300">
          GEN {generation.toString().padStart(4, '0')}
        </div>
      </div>

      <div className="bg-slate-950 rounded p-6 border border-slate-800 text-center relative overflow-hidden">
        {/* Background Grid */}
        <div 
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            backgroundImage: 'radial-gradient(circle, #f472b6 1px, transparent 1px)',
            backgroundSize: '20px 20px'
          }}
        ></div>

        <div className="relative z-10">
          <div className="text-xs text-slate-500 mb-2">CURRENT BEST EQUATION</div>
          <div className="text-2xl font-serif italic text-white mb-6">
            f(x) = {bestEq}
          </div>

          <div className="flex flex-col items-center">
            <div className="text-xs text-slate-400 mb-1 flex justify-between w-full max-w-[200px]">
              <span>FITNESS</span>
              <span className="font-mono text-pink-400">{fitness.toFixed(4)}</span>
            </div>
            
            <div className="w-full max-w-[200px] h-1.5 bg-slate-800 rounded overflow-hidden">
              <div 
                className="h-full bg-pink-500 transition-all duration-300 shadow-[0_0_8px_#ec4899]"
                style={{ width: `${fitness * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 flex gap-4 text-xs">
        <div className="flex-1 bg-slate-800 p-2 rounded text-center border border-slate-700 text-slate-400">
          <span className="block text-pink-500/80 mb-1">DIMENSIONAL</span>
          [M L T⁻²] Validated
        </div>
        <div className="flex-1 bg-slate-800 p-2 rounded text-center border border-slate-700 text-slate-400">
          <span className="block text-pink-500/80 mb-1">PARSIMONY</span>
          Penalty: -0.012
        </div>
      </div>

    </div>
  );
};
