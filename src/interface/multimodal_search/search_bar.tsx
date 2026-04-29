import React, { useState } from 'react';

export const SearchBar: React.FC = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<{id: string, type: string, score: number}[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = () => {
    if (!query) return;
    
    setIsSearching(true);
    setResults([]);
    
    // Deterministic simulation of multi-modal search delay and ranking
    setTimeout(() => {
      const hash = query.length;
      
      const newResults = [
        { id: `TXT-${hash * 2}`, type: 'Text', score: 0.95 },
        { id: `IMG-${hash * 3}`, type: 'Image', score: 0.88 },
        { id: `VID-${hash * 5}`, type: 'Video', score: 0.76 },
        { id: `AUD-${hash * 7}`, type: 'Audio', score: 0.62 }
      ];
      
      setResults(newResults);
      setIsSearching(false);
    }, 800);
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-10 p-6 bg-white rounded-xl shadow-xl border border-gray-200 font-sans">
      <div className="text-center mb-6">
        <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
          OMNI Multimodal Search
        </h1>
        <p className="text-sm text-gray-500 mt-2">Search across text, images, video, and audio simultaneously.</p>
      </div>

      <div className="flex space-x-2 mb-8">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Describe what you are looking for..."
          className="flex-1 px-4 py-3 rounded-lg border-2 border-gray-300 focus:border-blue-500 focus:outline-none transition-colors"
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button 
          onClick={handleSearch}
          disabled={isSearching}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-colors shadow-md disabled:bg-gray-400"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </button>
      </div>

      {results.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Top Matches</h3>
          {results.map((res, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 rounded-lg bg-gray-50 border border-gray-100 hover:bg-blue-50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className={`
                  w-10 h-10 rounded flex items-center justify-center text-white font-bold text-xs
                  ${res.type === 'Text' ? 'bg-blue-500' : 
                    res.type === 'Image' ? 'bg-purple-500' : 
                    res.type === 'Video' ? 'bg-pink-500' : 'bg-orange-500'}
                `}>
                  {res.type.substring(0,3).toUpperCase()}
                </div>
                <div>
                  <div className="font-bold text-gray-800">{res.id}</div>
                  <div className="text-xs text-gray-500">{res.type} Match</div>
                </div>
              </div>
              
              <div className="flex flex-col items-end">
                <div className="text-lg font-bold text-green-600">{(res.score * 100).toFixed(1)}%</div>
                <div className="w-24 h-2 bg-gray-200 rounded-full mt-1">
                  <div className="h-full bg-green-500 rounded-full" style={{ width: `${res.score * 100}%` }}></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
