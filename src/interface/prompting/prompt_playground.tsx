import React, { useState } from 'react';

interface PromptVariable {
    key: string;
    value: string;
}

export const OmniPromptPlayground: React.FC = () => {
    const [template, setTemplate] = useState<string>("Hello {{ name }}, translate this to {{ language }}: {{ text }}");
    const [variables, setVariables] = useState<PromptVariable[]>([
        { key: 'name', value: 'Alice' },
        { key: 'language', value: 'French' },
        { key: 'text', value: 'How does the Omni framework handle concurrency?' }
    ]);
    const [rendered, setRendered] = useState<string>('');
    const [error, setError] = useState<string | null>(null);

    // Simulate Python template engine bridging
    const handleRender = () => {
        try {
            setError(null);
            let result = template;
            
            // Regex to find missing variables
            const varPattern = /\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g;
            const matches = Array.from(template.matchAll(varPattern)).map(m => m[1]);
            
            const providedKeys = variables.map(v => v.key);
            const missing = matches.filter(m => !providedKeys.includes(m));
            
            if (missing.length > 0) {
                throw new Error(`Missing values for variables: ${missing.join(', ')}`);
            }

            variables.forEach(v => {
                const search = new RegExp(`\\{\\{\\s*${v.key}\\s*\\}\\}`, 'g');
                result = result.replace(search, v.value);
            });

            setRendered(result);
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Render failed');
            setRendered('');
        }
    };

    const handleAddVar = () => {
        setVariables([...variables, { key: `var_${variables.length}`, value: '' }]);
    };

    const handleUpdateVar = (index: number, field: 'key' | 'value', val: string) => {
        const newVars = [...variables];
        newVars[index][field] = val;
        setVariables(newVars);
    };

    return (
        <div className="omni-prompt-playground max-w-4xl mx-auto p-6 bg-slate-900 text-slate-200 rounded-xl shadow-2xl border border-slate-700">
            <h2 className="text-2xl font-bold text-sky-400 mb-6">Prompt Engine Playground</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Editor Side */}
                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-2">Template String</label>
                        <textarea 
                            className="w-full h-40 bg-slate-800 border border-slate-600 rounded p-3 font-mono text-sm focus:border-sky-500 outline-none"
                            value={template}
                            onChange={e => setTemplate(e.target.value)}
                        />
                    </div>

                    <div>
                        <div className="flex justify-between items-center mb-2">
                            <label className="text-sm font-medium text-slate-400">Variables</label>
                            <button onClick={handleAddVar} className="text-xs bg-slate-700 hover:bg-slate-600 px-2 py-1 rounded">
                                + Add Variable
                            </button>
                        </div>
                        <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                            {variables.map((v, i) => (
                                <div key={i} className="flex gap-2">
                                    <input 
                                        type="text" 
                                        placeholder="key"
                                        className="w-1/3 bg-slate-800 border border-slate-600 rounded px-2 py-1 font-mono text-sm"
                                        value={v.key}
                                        onChange={e => handleUpdateVar(i, 'key', e.target.value)}
                                    />
                                    <input 
                                        type="text" 
                                        placeholder="value"
                                        className="flex-1 bg-slate-800 border border-slate-600 rounded px-2 py-1 font-mono text-sm"
                                        value={v.value}
                                        onChange={e => handleUpdateVar(i, 'value', e.target.value)}
                                    />
                                </div>
                            ))}
                        </div>
                    </div>
                    
                    <button 
                        onClick={handleRender}
                        className="w-full bg-sky-600 hover:bg-sky-500 text-white font-bold py-2 px-4 rounded transition-colors"
                    >
                        Render Prompt
                    </button>
                </div>

                {/* Preview Side */}
                <div className="bg-slate-950 p-4 rounded-lg border border-slate-800">
                    <label className="block text-sm font-medium text-slate-500 mb-4 uppercase tracking-wider">Output Preview</label>
                    
                    {error && (
                        <div className="bg-red-900/30 border border-red-800 text-red-400 p-3 rounded mb-4 text-sm font-mono">
                            {error}
                        </div>
                    )}

                    <div className="whitespace-pre-wrap font-mono text-emerald-400 text-sm">
                        {rendered || <span className="text-slate-600 italic">Click render to preview...</span>}
                    </div>
                </div>
            </div>
        </div>
    );
};
