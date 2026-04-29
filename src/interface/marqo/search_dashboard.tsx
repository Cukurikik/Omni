import React, { useState, useEffect } from 'react';

/**
 * OMNI Interface Layer: Marqo Search Dashboard
 * Real-time dynamic visual search using React hooks.
 */

interface SearchResult {
    id: string;
    text: string;
    score: number;
    image_url?: string;
}

export const MarqoDashboard: React.FC = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const timeoutId = setTimeout(() => {
            if (query.trim() !== '') {
                executeSearch(query);
            } else {
                setResults([]);
            }
        }, 300); // Debounce

        return () => clearTimeout(timeoutId);
    }, [query]);

    const executeSearch = async (searchStr: string) => {
        setLoading(true);
        try {
            // Emulated production API hook to Omni Go router -> Rust Backend
            const response = await fetch('/api/marqo/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ q: searchStr, limit: 10 })
            });
            
            if (response.ok) {
                const data = await response.json();
                setResults(data.hits || []);
            }
        } catch (error) {
            console.error('[OMNI] Marqo search failed', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="omni-marqo-container p-6 bg-gray-900 min-h-screen text-white">
            <h1 className="text-3xl font-bold mb-6 text-blue-400">Marqo Tensor Search</h1>
            <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search images and text multimodally..."
                className="w-full p-4 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500 transition-colors"
            />
            
            {loading && <div className="mt-4 text-gray-400">Vectorizing query...</div>}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                {results.map((hit) => (
                    <div key={hit.id} className="bg-gray-800 rounded-xl overflow-hidden shadow-lg border border-gray-700 hover:border-blue-500 transition-colors cursor-pointer">
                        {hit.image_url && <img src={hit.image_url} alt="Result" className="w-full h-48 object-cover" />}
                        <div className="p-4">
                            <p className="text-gray-300 text-sm mb-2">Score: {(hit.score * 100).toFixed(2)}%</p>
                            <p className="text-white font-medium">{hit.text}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
