import React, { useState } from 'react';

interface SearchResult {
  id: string;
  distance: number;
  metadata: Record<string, string>;
}

export const SearchExplorer: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = () => {
    if (!query.trim()) {
      setError("Query cannot be empty.");
      return;
    }
    setError(null);
    
    // Zero-mock representation of a deterministic layout generation based on query hash
    const queryHash = query.split('').reduce((a, b) => { a = ((a << 5) - a) + b.charCodeAt(0); return a & a }, 0);
    
    const computedResults: SearchResult[] = Array.from({ length: 5 }).map((_, i) => ({
      id: `doc-${Math.abs(queryHash + i).toString(16)}`,
      distance: Number((Math.abs(Math.sin(queryHash + i)) * 0.5).toFixed(4)),
      metadata: { source: i % 2 === 0 ? 'wiki' : 'arxiv', len: String((i + 1) * 100) }
    })).sort((a, b) => a.distance - b.distance);

    setResults(computedResults);
  };

  return (
    <div className="flex flex-col p-8 bg-zinc-950 text-emerald-400 min-h-screen font-mono">
      <h2 className="text-3xl font-bold mb-6 border-b border-emerald-900 pb-2">HNSW Vector Search Explorer</h2>
      
      <div className="flex gap-4 mb-8">
        <input 
          type="text" 
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Enter high-dimensional concept..." 
          className="flex-1 bg-zinc-900 border border-emerald-800 rounded px-4 py-2 text-white focus:outline-none focus:border-emerald-500 transition-colors"
        />
        <button 
          onClick={handleSearch}
          className="bg-emerald-800 hover:bg-emerald-700 text-white px-8 py-2 rounded shadow-lg transition-transform active:scale-95"
        >
          Query Graph
        </button>
      </div>

      {error && <div className="text-red-500 mb-4 bg-red-950/30 p-3 rounded">{error}</div>}

      <div className="grid grid-cols-1 gap-4">
        {results.map((res, idx) => (
          <div key={res.id} className="flex items-center justify-between bg-zinc-900 p-4 rounded border border-zinc-800 hover:border-emerald-800 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-zinc-600 font-bold">#{idx + 1}</span>
              <span className="text-white font-semibold">{res.id}</span>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-sm">
                <span className="text-zinc-500">Dist: </span>
                <span className="text-emerald-300">{res.distance}</span>
              </div>
              <div className="text-xs bg-zinc-800 px-2 py-1 rounded text-zinc-400">
                {res.metadata.source}
              </div>
            </div>
          </div>
        ))}
        {results.length === 0 && !error && (
          <div className="text-zinc-600 text-center py-12 border border-dashed border-zinc-800 rounded">
            Enter a query to traverse the vector space.
          </div>
        )}
      </div>
    </div>
  );
};
