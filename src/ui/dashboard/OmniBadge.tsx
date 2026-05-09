import React from 'react';

// OmniBadge.tsx — Reusable UI Status Badge
// Layer: Interface / TypeScript
//
// A small but vital UI component for indicating status (Active, Error, Warning)
// across the dashboard. Enforces strict CSS variables and SVGs. Zero mock.

export type BadgeVariant = 'success' | 'warning' | 'error' | 'info' | 'neutral';

export interface OmniBadgeProps {
    label: string;
    variant?: BadgeVariant;
    icon?: React.ReactNode;
    className?: string;
    pulse?: boolean;
}

export const OmniBadge: React.FC<OmniBadgeProps> = ({
    label,
    variant = 'neutral',
    icon,
    className = '',
    pulse = false
}) => {
    
    // Variant maps ensuring consistent OMNI design language
    const colorMaps: Record<BadgeVariant, string> = {
        success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800/50',
        warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800/50',
        error:   'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200 dark:border-rose-800/50',
        info:    'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800/50',
        neutral: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    };
    
    const pulseMaps: Record<BadgeVariant, string> = {
        success: 'bg-emerald-500',
        warning: 'bg-amber-500',
        error:   'bg-rose-500',
        info:    'bg-blue-500',
        neutral: 'bg-slate-500',
    };

    return (
        <span className={`
            inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border
            ${colorMaps[variant]} 
            ${className}
        `}>
            {pulse && (
                <span className="flex w-2 h-2 mr-1.5 relative">
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${pulseMaps[variant]}`}></span>
                    <span className={`relative inline-flex rounded-full w-2 h-2 ${pulseMaps[variant]}`}></span>
                </span>
            )}
            
            {icon && !pulse && (
                <span className="mr-1.5">
                    {icon}
                </span>
            )}
            
            {label}
        </span>
    );
};
