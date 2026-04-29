import React, { useState, useEffect } from 'react';

export const SearchUI: React.FC = () => {
  const [results, setResults] = useState<{id: string, score: number, title: string}[]>([]);
  const [query, setQuery] = useState("");

  const papers = [
    "SARS-CoV-2 spike protein mutations",
    "CRISPR-Cas9 gene editing in oncology",
    "Deep learning for MRI segmentation",
    "Immunotherapy outcomes in melanoma"
  ];

  useEffect(() => {
    // Typing simulation
    const target = "COVID-19 Variants";
    let index = 0;
    const typeInterval = setInterval(() => {
      if (index <= target.length) {
        setQuery(target.substring(0, index));
        index++;
      } else {
        // Trigger search simulation
        setResults(papers.map((p, i) => ({
          id: `PMID-${1000 + i}`,
          score: 0.95 - (i * 0.15) + (Math.random() * 0.05),
          title: p
        })));
        clearInterval(typeInterval);
      }
    }, 150);

    return () => clearInterval(typeInterval);
  }, []);

  return (
    <div className="bg-slate-900 p-6 rounded-lg border border-slate-700 shadow-xl max-w-sm mx-auto font-sans text-slate-200">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-emerald-400">PaperAI Search</h2>
        <p className="text-xs text-slate-400">Medical Semantic + BM25</p>
      </div>

      <div className="bg-slate-950 p-3 rounded border border-slate-700 mb-4 flex items-center">
        <span className="text-slate-500 mr-2">🔍</span>
        <span className="font-mono text-emerald-300">{query}<span className="animate-pulse">|</span></span>
      </div>

      <div className="space-y-3">
        {results.map((r) => (
          <div key={r.id} className="bg-slate-800 p-3 rounded border border-slate-700 text-sm">
            <div className="flex justify-between items-start mb-1">
              <span className="font-bold text-blue-400 text-xs">{r.id}</span>
              <span className="bg-emerald-900 text-emerald-400 text-[10px] px-1 rounded font-mono">
                {(r.score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="text-slate-300 line-clamp-1">{r.title}</div>
          </div>
        ))}
        {results.length === 0 && query.length === "COVID-19 Variants".length && (
           <div className="text-center text-slate-500 text-xs py-4 animate-pulse">Searching 30M+ Papers...</div>
        )}
      </div>
    </div>
  );
};
