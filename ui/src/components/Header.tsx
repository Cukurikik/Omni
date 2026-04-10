import React from 'react';

interface HeaderProps {
    search: string;
    onSearchChange: (val: string) => void;
    onToggleSidebar: () => void;
    toolCount: number;
    totalCount: number;
}

export function OmniHeader({ search, onSearchChange, onToggleSidebar, toolCount, totalCount }: HeaderProps) {
    return (
        <header className="header">
            <div className="header-left">
                <button className="toggle-btn" onClick={onToggleSidebar} title="Toggle Sidebar">
                    ☰
                </button>
                <div className="header-info">
                    <h1 className="header-title">OMNI TOOLS</h1>
                    <span className="header-subtitle">
                        {toolCount} / {totalCount} tools aktif
                    </span>
                </div>
            </div>

            <div className="header-center">
                <div className="search-box">
                    <span className="search-icon">🔍</span>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Cari tool... (video_to_mp4, image_blur, dll)"
                        value={search}
                        onChange={e => onSearchChange(e.target.value)}
                    />
                    {search && (
                        <button className="search-clear" onClick={() => onSearchChange('')}>✕</button>
                    )}
                </div>
            </div>

            <div className="header-right">
                <div className="engine-badge">
                    <span className="badge-dot"></span>
                    <span>C++ · Go · Python · TS</span>
                </div>
            </div>
        </header>
    );
}