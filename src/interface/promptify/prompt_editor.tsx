import React, { useState } from 'react';

// OMNI TypeScript Interface Layer: Promptify Editor
// Reactive UI for building structured Output JSON Prompts.

interface PromptTemplate {
  systemInstruction: string;
  userQuery: string;
  requiredJsonKeys: string[];
}

export const PromptEditor: React.FC = () => {
  const [template, setTemplate] = useState<PromptTemplate>({
    systemInstruction: "You are an expert entity extractor. Extract data as JSON.",
    userQuery: "{text}",
    requiredJsonKeys: ["entities", "sentiment"]
  });

  const handleKeyAdd = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.currentTarget.value) {
      setTemplate({
        ...template,
        requiredJsonKeys: [...template.requiredJsonKeys, e.currentTarget.value]
      });
      e.currentTarget.value = '';
    }
  };

  const buildFinalPrompt = () => {
    const format = template.requiredJsonKeys.map(k => `"${k}": "..."`).join(",\n  ");
    return `${template.systemInstruction}\n\nStrictly return JSON in this format:\n{\n  ${format}\n}\n\nInput: ${template.userQuery}`;
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-slate-900 text-slate-200 rounded-xl shadow-2xl border border-slate-700">
      <h2 className="text-2xl font-bold mb-6 text-emerald-400">Promptify: Structured Output Engine</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">System Instruction</label>
          <textarea 
            className="w-full bg-slate-950 border border-slate-700 rounded p-3 text-slate-200 focus:border-emerald-500 focus:outline-none"
            value={template.systemInstruction}
            onChange={(e) => setTemplate({...template, systemInstruction: e.target.value})}
            rows={2}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-400 mb-1">Required JSON Keys (Press Enter to add)</label>
          <input 
            type="text" 
            placeholder="e.g. metadata"
            className="w-full bg-slate-950 border border-slate-700 rounded p-3 text-slate-200 focus:border-emerald-500 focus:outline-none mb-2"
            onKeyDown={handleKeyAdd}
          />
          <div className="flex flex-wrap gap-2">
            {template.requiredJsonKeys.map((key, idx) => (
              <span key={idx} className="bg-emerald-900/30 text-emerald-400 px-3 py-1 rounded-full text-sm border border-emerald-800">
                {key}
              </span>
            ))}
          </div>
        </div>

        <div className="pt-6 mt-6 border-t border-slate-800">
          <label className="block text-sm font-medium text-slate-400 mb-2">Compiled Final Prompt</label>
          <pre className="bg-slate-950 border border-slate-800 p-4 rounded text-sm text-cyan-400 overflow-x-auto font-mono whitespace-pre-wrap">
            {buildFinalPrompt()}
          </pre>
        </div>
      </div>
    </div>
  );
};
