import React, { useState } from 'react';

export const PromptEditor: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [generation, setGeneration] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    if (!prompt) return;
    setIsGenerating(true);
    setGeneration('');
    
    // Deterministic text generation via mathematical pseudo-randomness based on prompt length
    const words = ["The", "neural", "network", "processes", "information", "through", "layers", "of", "abstractions", "creating", "meaning", "from", "chaos."];
    let currentTokens = 0;
    const maxTokens = (prompt.length % 10) + 5;

    const interval = setInterval(() => {
      setGeneration(prev => prev + ' ' + words[currentTokens % words.length]);
      currentTokens++;
      if (currentTokens >= maxTokens) {
        clearInterval(interval);
        setIsGenerating(false);
      }
    }, 150);
  };

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-xl shadow-md border border-gray-100 font-sans">
      <h2 className="text-2xl font-bold text-indigo-600 mb-4">Texar Text Generation Interface</h2>
      
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
        <textarea 
          className="w-full border border-gray-300 rounded p-3 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition"
          rows={4}
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter prompt to initialize beam search..."
        />
      </div>

      <button 
        onClick={handleGenerate}
        disabled={isGenerating || !prompt}
        className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded hover:bg-indigo-700 disabled:opacity-50 transition"
      >
        {isGenerating ? 'Decoding...' : 'Generate Sequence'}
      </button>

      {generation && (
        <div className="mt-6 p-4 bg-indigo-50 border border-indigo-100 rounded text-gray-800 leading-relaxed">
          <strong>Output:</strong> {generation}
        </div>
      )}
    </div>
  );
};
