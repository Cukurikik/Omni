import React, { useState } from 'react';

interface Entity {
    id: string;
    start: number;
    end: number;
    label: string;
    text: string;
}

interface DocAnnotatorProps {
    initialText: string;
    initialEntities?: Entity[];
}

export const OmniDocAnnotator: React.FC<DocAnnotatorProps> = ({ initialText, initialEntities = [] }) => {
    const [text, setText] = useState(initialText);
    const [entities, setEntities] = useState<Entity[]>(initialEntities);
    const [selectedLabel, setSelectedLabel] = useState<string>('PER');

    const labels = [
        { id: 'PER', color: 'bg-blue-500/20 text-blue-300 border-blue-500' },
        { id: 'ORG', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500' },
        { id: 'LOC', color: 'bg-amber-500/20 text-amber-300 border-amber-500' },
        { id: 'MISC', color: 'bg-purple-500/20 text-purple-300 border-purple-500' },
    ];

    const handleMouseUp = () => {
        const selection = window.getSelection();
        if (!selection || selection.isCollapsed) return;

        // In a strict production environment, we use exact offset calculation within the div.
        // For structural demonstration, we simulate the text selection bounds.
        const selectedText = selection.toString();
        
        // Ensure valid text was selected
        if (selectedText.trim().length === 0) return;

        // Create new entity
        const newEntity: Entity = {
            id: Math.random().toString(36).substr(2, 9),
            start: 0, // Mock: real implementation requires node walking to find absolute offset
            end: selectedText.length,
            label: selectedLabel,
            text: selectedText
        };

        setEntities([...entities, newEntity]);
        selection.removeAllRanges();
    };

    const removeEntity = (id: string) => {
        setEntities(entities.filter(e => e.id !== id));
    };

    return (
        <div className="omni-doc-annotator max-w-5xl mx-auto p-6 bg-slate-900 rounded-xl border border-slate-700 shadow-2xl">
            <header className="mb-6 border-b border-slate-800 pb-4 flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-sky-400">Named Entity Annotation</h2>
                    <p className="text-sm text-slate-400 mt-1">Select text to tag entities for BERT-NER training</p>
                </div>
                <div className="flex gap-2">
                    {labels.map(l => (
                        <button
                            key={l.id}
                            onClick={() => setSelectedLabel(l.id)}
                            className={`px-3 py-1.5 rounded text-sm font-semibold border ${
                                selectedLabel === l.id 
                                    ? l.color + ' ring-2 ring-sky-500/50 ring-offset-2 ring-offset-slate-900' 
                                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700'
                            } transition-all`}
                        >
                            {l.id}
                        </button>
                    ))}
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-3">
                    <div 
                        className="bg-slate-950 p-6 rounded-lg border border-slate-800 text-slate-300 font-serif leading-relaxed text-lg min-h-[400px] selection:bg-sky-500/30"
                        onMouseUp={handleMouseUp}
                    >
                        {/* Structural mock of highlighted text rendering. 
                            Production requires splitting text into spans based on entity offsets. */}
                        {text}
                    </div>
                </div>

                <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                    <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-700 pb-2">Annotated Entities</h3>
                    {entities.length === 0 ? (
                        <div className="text-sm text-slate-500 italic text-center py-4">No entities tagged yet.</div>
                    ) : (
                        <ul className="space-y-3 max-h-[350px] overflow-y-auto pr-2">
                            {entities.map(e => {
                                const labelMeta = labels.find(l => l.id === e.label);
                                return (
                                    <li key={e.id} className="bg-slate-900 p-3 rounded border border-slate-700 flex flex-col gap-2 group">
                                        <div className="flex justify-between items-start">
                                            <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border ${labelMeta?.color}`}>
                                                {e.label}
                                            </span>
                                            <button 
                                                onClick={() => removeEntity(e.id)}
                                                className="text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                            >
                                                ✕
                                            </button>
                                        </div>
                                        <span className="text-sm text-slate-300 font-medium truncate" title={e.text}>
                                            {e.text}
                                        </span>
                                    </li>
                                );
                            })}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};
