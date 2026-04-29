import React, { useState } from 'react';

export const SearchBar: React.FC = () => {
    const [query, setQuery] = useState('');
    const [mode, setMode] = useState<'text' | 'image'>('text');

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        console.log(`Executing ${mode} search for: ${query}`);
    };

    const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setMode('image');
            setQuery(file.name);
            console.log(`Ready to search by image: ${file.name}`);
        }
    };

    return (
        <form onSubmit={handleSearch} style={{ display: 'flex', width: '100%', maxWidth: '600px', margin: '0 auto', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', borderRadius: '8px', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#f0f0f0', padding: '10px', display: 'flex', alignItems: 'center', borderRight: '1px solid #ccc' }}>
                <label style={{ cursor: 'pointer', margin: 0, padding: 0 }}>
                    📷
                    <input type="file" accept="image/*" onChange={handleImageUpload} style={{ display: 'none' }} />
                </label>
            </div>
            <input 
                type="text" 
                value={query} 
                onChange={(e) => { setQuery(e.target.value); setMode('text'); }} 
                placeholder={mode === 'image' ? "Image selected..." : "Search text or concepts..."}
                style={{ flex: 1, padding: '15px', border: 'none', outline: 'none', fontSize: '16px' }}
                readOnly={mode === 'image'}
            />
            <button type="submit" style={{ padding: '15px 25px', backgroundColor: '#6200ea', color: 'white', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>
                Search
            </button>
        </form>
    );
};
