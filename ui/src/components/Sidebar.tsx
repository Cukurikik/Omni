import React from 'react';
import { OmniLink } from '../omni';

interface SidebarProps {
    categories: { id: string; label: string; emoji: string }[];
    activeCategory: string;
    onCategoryChange: (cat: any) => void;
    isOpen: boolean;
    categoryCounts: Record<string, number>;
}

export function OmniSidebar({ categories, activeCategory, onCategoryChange, isOpen, categoryCounts }: SidebarProps) {
    if (!isOpen) return null;

    return (
        <aside className="sidebar">
            <OmniLink to="/" className="sidebar-logo">
                <span className="logo-icon">⚡</span>
                <span className="logo-text">OMNI</span>
                <span className="logo-version">v2.0</span>
            </OmniLink>

            <nav className="sidebar-nav">
                <div className="nav-section-title">KATEGORI</div>
                {categories.map(cat => (
                    <button
                        key={cat.id}
                        className={`nav-item ${activeCategory === cat.id ? 'active' : ''}`}
                        onClick={() => onCategoryChange(cat.id)}
                    >
                        <span className="nav-emoji">{cat.emoji}</span>
                        <span className="nav-label">{cat.label}</span>
                        <span className="nav-count">{categoryCounts[cat.id] || 0}</span>
                    </button>
                ))}
            </nav>

            <div className="sidebar-footer">
                <OmniLink to="/settings" className="footer-link">⚙️ Settings</OmniLink>
                <div className="status-indicator">
                    <span className="status-dot"></span>
                    <span>Gateway Online</span>
                </div>
            </div>
        </aside>
    );
}
