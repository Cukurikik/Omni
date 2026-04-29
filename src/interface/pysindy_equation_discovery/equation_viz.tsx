import React, { useState, useEffect } from 'react';

export const EquationViz: React.FC = () => {
  const [equation, setEquation] = useState("ẋ = 1.000 x");
  const [iteration, setIteration] = useState(0);

  useEffect(() => {
    const equations = [
      "ẋ = 1.2 x + 0.5 y - 0.1 x² + 0.05 xy - 0.01 y³", // dense
      "ẋ = 1.0 x + 0.5 y - 0.1 x²",                     // stlsq iteration 1
      "ẋ = 1.0 x + 0.5 y",                              // stlsq iteration 2
      "ẋ = σ(y - x)",                                   // final lorenz
      "ẏ = x(ρ - z) - y",
      "ż = xy - βz"
    ];

    const interval = setInterval(() => {
      setIteration(prev => {
        const next = prev + 1;
        if (next < equations.length) {
          setEquation(equations[next]);
        }
        return next;
      });
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 border-b border-slate-700 pb-2">
        <h2 className="text-xl font-bold text-fuchsia-500">PySINDy AI</h2>
        <p className="text-xs text-slate-400">Data-Driven Equation Discovery</p>
      </div>

      <div className="bg-slate-950 p-4 rounded border border-slate-800 flex items-center justify-center min-h-[100px]">
        <div className="font-serif text-xl tracking-wider text-white">
           {equation}
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center text-xs font-mono text-slate-500">
        <div>STLSQ Iteration: {Math.min(iteration, 5)}</div>
        <div className="text-fuchsia-500 font-bold">
          {iteration >= 3 ? 'CONVERGED: LORENZ SYSTEM' : 'OPTIMIZING...'}
        </div>
      </div>
    </div>
  );
};
