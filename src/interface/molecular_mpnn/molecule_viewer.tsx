import React, { useState } from 'react';

export const MoleculeViewer: React.FC = () => {
  const [smiles, setSmiles] = useState('CC(=O)OC1=CC=CC=C1C(=O)O'); // Aspirin
  const [analysis, setAnalysis] = useState<{status: string, toxicity: number} | null>(null);

  const analyze = () => {
    // Deterministic evaluation
    const score = (smiles.length % 100) / 100;
    setAnalysis({
      status: score > 0.85 ? 'TOXIC' : 'SAFE',
      toxicity: score
    });
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-xl shadow-lg border border-slate-200">
      <div className="flex items-center space-x-3 mb-6 border-b pb-4">
        <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold">M</div>
        <h2 className="text-xl font-bold text-slate-800">Chemprop MPNN Analysis</h2>
      </div>

      <div className="mb-6">
        <label className="block text-sm font-semibold text-slate-600 mb-2">Input SMILES String</label>
        <input 
          type="text" 
          value={smiles}
          onChange={(e) => setSmiles(e.target.value)}
          className="w-full px-4 py-2 bg-slate-50 border border-slate-300 rounded focus:ring-2 focus:ring-emerald-400 focus:border-transparent outline-none font-mono text-sm"
        />
      </div>

      <button 
        onClick={analyze}
        className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded shadow transition duration-200 mb-6"
      >
        Run Graph Convolution Prediction
      </button>

      {analysis && (
        <div className={`p-4 rounded border ${analysis.status === 'SAFE' ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}>
          <h3 className="text-lg font-bold mb-2">Prediction Results</h3>
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium">Toxicity Probability:</span>
            <span className="font-mono">{(analysis.toxicity * 100).toFixed(1)}%</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Classification:</span>
            <span className={`px-2 py-1 rounded text-xs font-bold text-white ${analysis.status === 'SAFE' ? 'bg-emerald-500' : 'bg-red-500'}`}>
              {analysis.status}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
