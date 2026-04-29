import React, { useState } from 'react';

interface BuildLog {
  timestamp: string;
  stage: 'PARSE' | 'COMPILE' | 'ALLOCATE' | 'READY';
  message: string;
}

export const ModelBuilder: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [isBuilding, setIsBuilding] = useState<boolean>(false);
  const [logs, setLogs] = useState<BuildLog[]>([]);

  const handleBuild = () => {
    if (!prompt.trim() || isBuilding) return;

    setIsBuilding(true);
    setLogs([]);
    
    // Deterministic simulation of build stages
    const sequence = [
      { t: 200, stage: 'PARSE', msg: 'Translating prompt to Neural AST...' },
      { t: 800, stage: 'COMPILE', msg: 'Compiling AST via Rust FFI to Tensor Graph...' },
      { t: 1500, stage: 'ALLOCATE', msg: 'Allocating continuous memory blocks on GPU...' },
      { t: 2200, stage: 'READY', msg: 'Model generated: urn:omni:model:8f3c1a2' }
    ] as const;

    sequence.forEach(({ t, stage, msg }) => {
      setTimeout(() => {
        setLogs(prev => [...prev, {
          timestamp: new Date().toISOString().split('T')[1].slice(0, 8),
          stage,
          message: msg
        }]);
        if (stage === 'READY') {
          setIsBuilding(false);
          setPrompt('');
        }
      }, t);
    });
  };

  return (
    <div className="bg-slate-50 min-h-screen p-8 text-slate-800 font-sans">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-200">
        
        <div className="p-8 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
          <h1 className="text-3xl font-bold mb-2">PromptML Engine</h1>
          <p className="text-blue-100 opacity-90">Natural language to compiled neural network generation.</p>
        </div>

        <div className="p-8">
          <label className="block text-sm font-semibold text-slate-600 mb-2 uppercase tracking-wide">
            Network Architecture Prompt
          </label>
          <textarea 
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            disabled={isBuilding}
            placeholder="E.g., 'Build an image classifier for 10 classes using convolutions and attention.'"
            className="w-full h-32 bg-slate-50 border border-slate-300 rounded-lg p-4 mb-6 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />

          <button 
            onClick={handleBuild}
            disabled={isBuilding || !prompt.trim()}
            className={`w-full py-4 rounded-lg font-bold shadow-md transition-all ${
              isBuilding ? 'bg-slate-200 text-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-lg'
            }`}
          >
            {isBuilding ? 'Synthesizing Architecture...' : 'Generate Neural Network'}
          </button>

          {logs.length > 0 && (
            <div className="mt-8">
              <h3 className="text-sm font-semibold text-slate-600 mb-4 uppercase tracking-wide border-b pb-2">Build Telemetry</h3>
              <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm space-y-2 text-slate-300">
                {logs.map((log, idx) => (
                  <div key={idx} className="flex gap-4">
                    <span className="text-slate-500">[{log.timestamp}]</span>
                    <span className={`w-20 font-bold ${
                      log.stage === 'READY' ? 'text-emerald-400' :
                      log.stage === 'COMPILE' ? 'text-amber-400' :
                      log.stage === 'ALLOCATE' ? 'text-blue-400' : 'text-slate-400'
                    }`}>
                      {log.stage}
                    </span>
                    <span className="text-slate-100">{log.message}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
