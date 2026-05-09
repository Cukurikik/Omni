import React from 'react';

// OmniSidebar.tsx — Application Sidebar Navigation
// Layer: Interface / TypeScript
//
// Responsive, accessible side navigation component for the OMNI Dashboard.
// Handles active states, routing context simulation, and theme compatibility.

export interface NavItem {
    id: string;
    label: string;
    icon?: React.ReactNode;
    href: string;
}

export interface OmniSidebarProps {
    items: NavItem[];
    activeId: string;
    onNavigate: (id: string, href: string) => void;
    collapsed?: boolean;
}

export const OmniSidebar: React.FC<OmniSidebarProps> = ({
    items,
    activeId,
    onNavigate,
    collapsed = false
}) => {
    
    return (
        <aside 
            className={`
                h-screen bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800
                transition-all duration-300 ease-in-out flex flex-col
                ${collapsed ? 'w-20' : 'w-64'}
            `}
            aria-label="Sidebar Navigation"
        >
            <div className="flex items-center justify-center h-16 border-b border-slate-200 dark:border-slate-800">
                <span className={`font-black text-xl tracking-tighter text-blue-600 dark:text-blue-400 ${collapsed ? 'hidden' : 'block'}`}>
                    OMNI
                </span>
                {collapsed && (
                    <span className="font-black text-xl tracking-tighter text-blue-600 dark:text-blue-400">
                        O
                    </span>
                )}
            </div>

            <nav className="flex-1 overflow-y-auto py-4">
                <ul className="space-y-1 px-3">
                    {items.map((item) => {
                        const isActive = item.id === activeId;
                        return (
                            <li key={item.id}>
                                <button
                                    onClick={() => onNavigate(item.id, item.href)}
                                    className={`
                                        w-full flex items-center rounded-lg px-3 py-2.5 transition-colors
                                        ${isActive 
                                            ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300' 
                                            : 'text-slate-600 hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-800'
                                        }
                                        ${collapsed ? 'justify-center' : 'justify-start'}
                                    `}
                                    aria-current={isActive ? 'page' : undefined}
                                >
                                    {item.icon && (
                                        <span className={`flex-shrink-0 ${isActive ? 'text-blue-600 dark:text-blue-400' : ''}`}>
                                            {item.icon}
                                        </span>
                                    )}
                                    {!collapsed && (
                                        <span className="ml-3 font-medium text-sm">
                                            {item.label}
                                        </span>
                                    )}
                                </button>
                            </li>
                        );
                    })}
                </ul>
            </nav>
            
            <div className="p-4 border-t border-slate-200 dark:border-slate-800">
                {!collapsed ? (
                    <div className="text-xs text-slate-500 text-center">
                        OMNI Engine v3.0
                    </div>
                ) : (
                    <div className="text-xs text-slate-500 text-center">
                        v3
                    </div>
                )}
            </div>
        </aside>
    );
};
