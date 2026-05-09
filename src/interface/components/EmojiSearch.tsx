//=============================================================================
// OMNI INTERFACE LAYER — EMOJI SEMANTIC SEARCH (TYPESCRIPT / REACT)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: UI for searching emojis semantically in 50+ languages.
//=============================================================================

import React, { useState } from 'react';
import { NetworkClient } from '@omni-bridge/network';

/**
 * @html_template("emojeez-search")
 */
export const EmojiSearch: React.FC = () => {
    const [query, setQuery] = useState('');
    const [emojis, setEmojis] = useState<string[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSearch = async () => {
        if (!query) return;
        
        setIsLoading(true);
        
        // Dispatches to C# Domain -> Rust Search Engine -> Qdrant
        const result = await NetworkClient.graphqlQuery<{results: string[]}>('searchEmojis', {
            text: query,
            limit: 10
        });

        if (result.isOk()) {
            setEmojis(result.unwrap().results);
        } else {
            console.error("Failed to search emojis:", result.getError());
        }
        
        setIsLoading(false);
    };

    return (
        <div className="p-8 max-w-2xl mx-auto bg-gray-900 rounded-xl shadow-2xl text-white">
            <h1 className="text-3xl font-bold mb-4 text-center text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-red-500">
                Emojeez Semantic Search
            </h1>
            
            <div className="flex space-x-4 mb-8">
                <input 
                    type="text" 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Describe an emotion, object, or concept..."
                    className="flex-1 p-4 bg-gray-800 border border-gray-700 rounded-lg focus:ring-2 focus:ring-yellow-500 text-white outline-none"
                />
                <button 
                    onClick={handleSearch}
                    disabled={isLoading}
                    className="px-6 py-4 bg-yellow-500 hover:bg-yellow-600 text-black font-bold rounded-lg transition-colors disabled:opacity-50"
                >
                    {isLoading ? 'Searching...' : 'Search'}
                </button>
            </div>

            <div className="flex flex-wrap gap-4 justify-center">
                {emojis.map((emoji, idx) => (
                    <div 
                        key={idx} 
                        className="text-6xl p-4 bg-gray-800 rounded-2xl hover:scale-110 transition-transform cursor-pointer shadow-lg"
                        title="Copy to clipboard"
                        onClick={() => navigator.clipboard.writeText(emoji)}
                    >
                        {emoji}
                    </div>
                ))}
            </div>
            
            {emojis.length === 0 && !isLoading && query && (
                <p className="text-center text-gray-500">No emojis found. Try another description.</p>
            )}
        </div>
    );
};
