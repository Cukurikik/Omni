import React from 'react';

// OmniCard.tsx — Reusable UI Card
// Layer: Interface / TypeScript
//
// A high-quality, reusable glassmorphic card component for the OMNI Dashboard.
// Implements strict styling adherence to the OMNI design system.

export interface OmniCardProps {
    title?: string;
    subtitle?: string;
    children: React.ReactNode;
    className?: string;
    onClick?: () => void;
    hoverEffect?: boolean;
}

export const OmniCard: React.FC<OmniCardProps> = ({
    title,
    subtitle,
    children,
    className = '',
    onClick,
    hoverEffect = false,
}) => {
    
    // Core Tailwind classes combined with dynamic styling
    const baseClasses = `
        bg-white dark:bg-slate-800 
        border border-slate-200 dark:border-slate-700 
        rounded-xl shadow-sm overflow-hidden
        transition-all duration-300 ease-in-out
    `;
    
    const hoverClasses = hoverEffect 
        ? 'hover:shadow-md hover:border-slate-300 dark:hover:border-slate-600 hover:-translate-y-1 cursor-pointer' 
        : '';
        
    const clickableProps = onClick ? { onClick, role: 'button', tabIndex: 0 } : {};

    return (
        <div 
            className={`${baseClasses} ${hoverClasses} ${className}`.trim()} 
            {...clickableProps}
        >
            {(title || subtitle) && (
                <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-700/50">
                    {title && (
                        <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100 tracking-tight">
                            {title}
                        </h3>
                    )}
                    {subtitle && (
                        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                            {subtitle}
                        </p>
                    )}
                </div>
            )}
            
            <div className="p-6">
                {children}
            </div>
        </div>
    );
};
