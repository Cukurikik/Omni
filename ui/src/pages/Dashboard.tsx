import React, { useState, useMemo } from 'react';
import { OMNI_TOOLS_UI, OmniCategory } from '../configs/toolsMap';
import { OmniToolCard } from '../components/ToolCard';

const CATEGORIES: { id: OmniCategory | 'ALL'; label: string; emoji: string }[] = [
    { id: 'ALL', label: 'Semua', emoji: '🌐' },
    { id: 'VIDEO', label: 'Video', emoji: '🎬' },
    { id: 'AUDIO', label: 'Audio', emoji: '🎵' },
    { id: 'IMAGE', label: 'Image', emoji: '🖼️' },
    { id: 'PDF', label: 'PDF', emoji: '📄' },
    { id: 'CONVERTER', label: 'Converter', emoji: '🔄' },
    { id: 'AI', label: 'AI', emoji: '✨' },
    { id: 'LLM', label: 'LLM', emoji: '🤖' },
    { id: 'SYSTEM', label: 'System', emoji: '⚙️' },
];

export function OmniDashboard() {
    const [category, setCategory] = useState<OmniCategory | 'ALL'>('ALL');
    const [search, setSearch] = useState('');

    const filteredTools = useMemo(() => {
        return OMNI_TOOLS_UI.filter(t => {
            const matchCat = category === 'ALL' || t.category === category;
            const matchSearch = search === '' ||
                t.name.toLowerCase().includes(search.toLowerCase()) ||
                t.id.toLowerCase().includes(search.toLowerCase());
            return matchCat && matchSearch;
        });
    }, [category, search]);

    const categoryCounts = useMemo(() => {
        const c: Record<string, number> = { ALL: OMNI_TOOLS_UI.length };
        OMNI_TOOLS_UI.forEach(t => { c[t.category] = (c[t.category] || 0) + 1; });
        return c;
    }, []);

    return (
        <div className="dashboard">
            {/* Category Filter Bar */}
            <div className="category-bar">
                {CATEGORIES.map(cat => (
                    <button
                        key={cat.id}
                        className={`cat-btn ${category === cat.id ? 'active' : ''}`}
                        onClick={() => setCategory(cat.id)}
                    >
                        <span>{cat.emoji}</span>
                        <span>{cat.label}</span>
                        <span className="cat-count">{categoryCounts[cat.id] || 0}</span>
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="dash-search">
                <span className="search-icon">🔍</span>
                <input
                    type="text"
                    className="search-input"
                    placeholder="Cari tool... (contoh: video_to_mp4, image_blur)"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                {search && (
                    <button className="search-clear" onClick={() => setSearch('')}>✕</button>
                )}
            </div>

            {/* Stats */}
            <div className="dash-stats">
                <div className="stat-card">
                    <span className="stat-num">{OMNI_TOOLS_UI.length}</span>
                    <span className="stat-label">Total Tools</span>
                </div>
                <div className="stat-card">
                    <span className="stat-num">{categoryCounts['VIDEO'] || 0}</span>
                    <span className="stat-label">Video</span>
                </div>
                <div className="stat-card">
                    <span className="stat-num">{categoryCounts['AUDIO'] || 0}</span>
                    <span className="stat-label">Audio</span>
                </div>
                <div className="stat-card">
                    <span className="stat-num">{categoryCounts['IMAGE'] || 0}</span>
                    <span className="stat-label">Image</span>
                </div>
                <div className="stat-card">
                    <span className="stat-num">{categoryCounts['PDF'] || 0}</span>
                    <span className="stat-label">PDF</span>
                </div>
            </div>

            {/* Tool Grid */}
            <div className="tools-grid">
                {filteredTools.map(tool => (
                    <OmniToolCard key={tool.id} tool={tool} />
                ))}
                {filteredTools.length === 0 && (
                    <div className="empty-state">
                        <span className="empty-icon">🔍</span>
                        <p>Tidak ada tool yang cocok.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
