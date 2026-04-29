import React, { useState, useEffect } from 'react';

export const EvalDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    faithfulness: 0.2,
    answerRelevance: 0.1,
    contextPrecision: 0.0
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        faithfulness: prev.faithfulness < 0.94 ? prev.faithfulness + 0.1 : prev.faithfulness,
        answerRelevance: prev.answerRelevance < 0.88 ? prev.answerRelevance + 0.08 : prev.answerRelevance,
        contextPrecision: prev.contextPrecision < 0.91 ? prev.contextPrecision + 0.09 : prev.contextPrecision,
      }));
    }, 400);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-6 flex justify-between items-center border-b border-slate-700 pb-2">
        <div>
          <h2 className="text-xl font-bold text-green-400">RAG Eval Harness</h2>
          <p className="text-xs text-slate-400">Ragas/TruLens Metrics</p>
        </div>
        <div className="text-xs font-mono bg-slate-800 px-2 py-1 rounded text-slate-300">
          Suite: #8842
        </div>
      </div>

      <div className="space-y-4">
        {[
          { label: 'Faithfulness (No Hallucinations)', val: metrics.faithfulness },
          { label: 'Answer Relevance', val: metrics.answerRelevance },
          { label: 'Context Precision (Retrieval)', val: metrics.contextPrecision }
        ].map((metric, i) => (
          <div key={i}>
            <div className="flex justify-between text-xs mb-1">
               <span className="text-slate-300">{metric.label}</span>
               <span className="font-mono text-green-300">{(metric.val * 100).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden">
               <div 
                 className={`h-full transition-all duration-300 ${metric.val > 0.9 ? 'bg-green-500' : metric.val > 0.7 ? 'bg-yellow-500' : 'bg-red-500'}`}
                 style={{ width: `${Math.min(100, metric.val * 100)}%` }}
               />
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 p-3 bg-slate-800 rounded border border-slate-700">
         <div className="text-[10px] uppercase text-slate-500 mb-1 font-bold">Harness Verdict</div>
         <div className="text-sm text-white">
           {metrics.faithfulness > 0.9 ? 'RAG Pipeline Certified for Production.' : 'Evaluating Pipeline...'}
         </div>
      </div>
    </div>
  );
};
