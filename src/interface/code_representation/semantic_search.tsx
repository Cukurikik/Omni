import React, { useState } from 'react';

export const SemanticSearch: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<string[]>([]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    // Deterministic semantic results based on query length and chars
    const baseHash = query.length + query.charCodeAt(0);
    const fakeResults = [
      `src/utils/parser.ts (Score: ${(baseHash % 100) / 100 + 0.5})`,
      `lib/core/ast.rs (Score: ${(baseHash % 50) / 100 + 0.4})`,
      `models/embedder.py (Score: ${(baseHash % 25) / 100 + 0.3})`
    ];

    setResults(fakeResults);
  };

  return (
    <div className="p-6 max-w-2xl mx-auto bg-gray-50 border border-gray-200 rounded-lg shadow font-sans">
      <h2 className="text-2xl font-bold mb-4 text-blue-600">CodeSearchNet Explorer</h2>
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for semantic code representations..."
          className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Search
        </button>
      </form>

      <div className="space-y-3">
        {results.map((res, i) => (
          <div key={i} className="p-4 bg-white border rounded shadow-sm flex items-center justify-between">
            <span className="font-mono text-gray-800">{res.split(' (')[0]}</span>
            <span className="text-sm font-bold text-green-600">({res.split('(')[1]}</span>
          </div>
        ))}
        {results.length === 0 && (
          <p className="text-gray-500 text-center py-8">Enter a query to search codebase.</p>
        )}
      </div>
    </div>
  );
};
