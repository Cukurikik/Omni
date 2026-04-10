import React from 'react';
import { omniNavigate } from '../omni';
import type { OmniToolUI } from '../configs/toolsMap';

interface ToolCardProps {
    tool: OmniToolUI;
}

const CATEGORY_COLORS: Record<string, string> = {
    VIDEO: '#6366f1',
    AUDIO: '#ec4899',
    IMAGE: '#f59e0b',
    PDF: '#ef4444',
    CONVERTER: '#10b981',
    AI: '#8b5cf6',
    LLM: '#06b6d4',
    SYSTEM: '#64748b',
};

const CATEGORY_EMOJI: Record<string, string> = {
    VIDEO: '🎬',
    AUDIO: '🎵',
    IMAGE: '🖼️',
    PDF: '📄',
    CONVERTER: '🔄',
    AI: '✨',
    LLM: '🤖',
    SYSTEM: '⚙️',
};

export function OmniToolCard({ tool }: ToolCardProps) {
    const color = CATEGORY_COLORS[tool.category] || '#64748b';
    const emoji = CATEGORY_EMOJI[tool.category] || '🔧';

    const handleClick = () => {
        omniNavigate(`/tool/${tool.id}`);
    };

    return (
        <button
            className="tool-card"
            onClick={handleClick}
            style={{ '--accent': color } as React.CSSProperties}
        >
            <div className="tool-card-header">
                <span className="tool-emoji">{emoji}</span>
                <span className="tool-category" style={{ background: color }}>
                    {tool.category}
                </span>
            </div>
            <h3 className="tool-name">{tool.name}</h3>
            <p className="tool-desc">{tool.description}</p>
            <div className="tool-footer">
                <span className="tool-id">{tool.id}</span>
                <span className="tool-arrow">→</span>
            </div>
        </button>
    );
}
