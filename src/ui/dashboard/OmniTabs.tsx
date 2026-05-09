import React, { useState } from 'react';

// OmniTabs.tsx — Accessible UI Tabs
// Layer: Interface / TypeScript
//
// A fully accessible, keyboard-navigable tab component. Strict layout 
// preservation and active state tracking. Zero mock.

export interface TabItem {
    id: string;
    label: string;
    content: React.ReactNode;
    icon?: React.ReactNode;
    disabled?: boolean;
}

export interface OmniTabsProps {
    tabs: TabItem[];
    defaultTabId?: string;
    onChange?: (tabId: string) => void;
    className?: string;
    variant?: 'line' | 'pills';
}

export const OmniTabs: React.FC<OmniTabsProps> = ({
    tabs,
    defaultTabId,
    onChange,
    className = '',
    variant = 'line'
}) => {
    
    // Auto-select first non-disabled tab if default not provided
    const initialTab = defaultTabId || tabs.find(t => !t.disabled)?.id || tabs[0]?.id;
    const [activeTabId, setActiveTabId] = useState<string>(initialTab);

    const handleTabClick = (id: string, disabled?: boolean) => {
        if (disabled) return;
        setActiveTabId(id);
        if (onChange) onChange(id);
    };

    const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
        let newIndex = index;
        if (e.key === 'ArrowRight') {
            newIndex = index + 1 >= tabs.length ? 0 : index + 1;
        } else if (e.key === 'ArrowLeft') {
            newIndex = index - 1 < 0 ? tabs.length - 1 : index - 1;
        } else {
            return;
        }

        // Skip disabled tabs
        while (tabs[newIndex].disabled) {
            newIndex = e.key === 'ArrowRight' 
                ? (newIndex + 1 >= tabs.length ? 0 : newIndex + 1)
                : (newIndex - 1 < 0 ? tabs.length - 1 : newIndex - 1);
            
            // Break infinite loop if all other tabs are disabled
            if (newIndex === index) return; 
        }

        const newId = tabs[newIndex].id;
        setActiveTabId(newId);
        if (onChange) onChange(newId);
        
        // Set focus to the new tab button
        const btn = document.getElementById(`omni-tab-${newId}`);
        if (btn) btn.focus();
    };

    const activeContent = tabs.find(t => t.id === activeTabId)?.content;

    return (
        <div className={`w-full ${className}`}>
            <div 
                className={`flex space-x-1 ${variant === 'line' ? 'border-b border-slate-200 dark:border-slate-700' : 'bg-slate-100 dark:bg-slate-800 p-1 rounded-xl'}`}
                role="tablist"
                aria-orientation="horizontal"
            >
                {tabs.map((tab, index) => {
                    const isActive = tab.id === activeTabId;
                    
                    let tabClasses = "flex items-center justify-center px-4 py-2.5 text-sm font-medium transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ";
                    
                    if (variant === 'line') {
                        tabClasses += isActive 
                            ? "border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400 "
                            : "border-b-2 border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-300 ";
                    } else {
                        // Pills
                        tabClasses += "rounded-lg " + (isActive 
                            ? "bg-white text-slate-800 shadow-sm dark:bg-slate-700 dark:text-white "
                            : "text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-white/50 dark:hover:bg-slate-700/50 ");
                    }

                    if (tab.disabled) {
                        tabClasses += "opacity-50 cursor-not-allowed hover:text-slate-500";
                    }

                    return (
                        <button
                            key={tab.id}
                            id={`omni-tab-${tab.id}`}
                            role="tab"
                            aria-selected={isActive}
                            aria-controls={`omni-tabpanel-${tab.id}`}
                            disabled={tab.disabled}
                            tabIndex={isActive ? 0 : -1}
                            onClick={() => handleTabClick(tab.id, tab.disabled)}
                            onKeyDown={(e) => handleKeyDown(e, index)}
                            className={tabClasses}
                        >
                            {tab.icon && <span className="mr-2">{tab.icon}</span>}
                            {tab.label}
                        </button>
                    );
                })}
            </div>
            
            <div 
                id={`omni-tabpanel-${activeTabId}`}
                role="tabpanel"
                aria-labelledby={`omni-tab-${activeTabId}`}
                className="pt-4 focus:outline-none"
                tabIndex={0}
            >
                {activeContent}
            </div>
        </div>
    );
};
