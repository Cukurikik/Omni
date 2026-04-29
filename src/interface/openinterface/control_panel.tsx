import React, { useState } from 'react';

export const ControlPanel: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);
  const [activeActions, setActiveActions] = useState<number>(0);

  const handleExecute = () => {
    if (!prompt.trim()) return;

    setActiveActions(prev => prev + 1);
    setLogs(prev => [`[${new Date().toLocaleTimeString()}] LLM Interpreting: "${prompt}"`, ...prev].slice(0, 10));
    
    // Simulated determinism for UI responsiveness
    setTimeout(() => {
      const generatedPlan = prompt.length > 10 ? 'Plan[Browser, Mouse_Click]' : 'Plan[Keyboard_Type]';
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Action Sequence Generated: ${generatedPlan}`, ...prev].slice(0, 10));
      setActiveActions(prev => prev - 1);
    }, 400);

    setPrompt('');
  };

  return (
    <div className="flex flex-col p-8 bg-zinc-900 text-amber-500 min-h-screen font-mono">
      <h2 className="text-3xl font-bold mb-6 border-b border-amber-800 pb-2">Omni Open-Interface Control Panel</h2>
      
      <div className="flex flex-col gap-4 mb-8">
        <textarea 
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Describe action for LLM (e.g., 'Open browser and click search')..." 
          className="w-full h-32 bg-zinc-800 border border-amber-900 rounded p-4 text-white focus:outline-none focus:border-amber-500 resize-none transition-colors"
        />
        <button 
          onClick={handleExecute}
          disabled={activeActions > 0}
          className={`px-8 py-3 rounded shadow-lg transition-all ${
            activeActions > 0 ? 'bg-zinc-700 text-zinc-500 cursor-not-allowed' : 'bg-amber-700 hover:bg-amber-600 text-white'
          }`}
        >
          {activeActions > 0 ? 'Executing Sequence...' : 'Dispatch Instruction'}
        </button>
      </div>

      <div className="bg-zinc-950 border border-amber-900 rounded p-4 flex-1">
        <h3 className="text-lg text-amber-300 mb-4">Execution Logs</h3>
        <div className="space-y-2">
          {logs.map((log, idx) => (
            <div key={idx} className="text-sm text-amber-100/80 border-l-2 border-amber-700 pl-2">
              {log}
            </div>
          ))}
          {logs.length === 0 && (
            <div className="text-zinc-600 italic">No actions executed yet.</div>
          )}
        </div>
      </div>
    </div>
  );
};
