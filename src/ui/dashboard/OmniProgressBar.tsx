import React from 'react';

// OmniProgressBar.tsx — Reusable UI Progress Bar
// Layer: Interface / TypeScript
//
// A responsive, animated progress bar supporting precise percentages and
// conditional color mapping based on threshold states. Zero mock.

export interface OmniProgressBarProps {
    progress: number; // 0 to 100
    label?: string;
    showValue?: boolean;
    height?: 'sm' | 'md' | 'lg';
    colorMode?: 'primary' | 'success' | 'warning' | 'danger' | 'auto';
    className?: string;
}

export const OmniProgressBar: React.FC<OmniProgressBarProps> = ({
    progress,
    label,
    showValue = true,
    height = 'md',
    colorMode = 'primary',
    className = ''
}) => {
    // Ensure bounds
    const clampedProgress = Math.min(100, Math.max(0, progress));

    const heightClasses = {
        sm: 'h-1.5',
        md: 'h-2.5',
        lg: 'h-4'
    };

    const determineColor = () => {
        if (colorMode !== 'auto') {
            switch (colorMode) {
                case 'success': return 'bg-emerald-500';
                case 'warning': return 'bg-amber-500';
                case 'danger': return 'bg-rose-500';
                default: return 'bg-blue-600 dark:bg-blue-500';
            }
        }
        
        // Auto color mode based on percentage thresholds
        if (clampedProgress >= 90) return 'bg-rose-500';
        if (clampedProgress >= 75) return 'bg-amber-500';
        return 'bg-emerald-500';
    };

    const fillColor = determineColor();

    return (
        <div className={`w-full ${className}`}>
            {(label || showValue) && (
                <div className="flex justify-between items-end mb-1">
                    {label && (
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {label}
                        </span>
                    )}
                    {showValue && (
                        <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 tabular-nums">
                            {Math.round(clampedProgress)}%
                        </span>
                    )}
                </div>
            )}
            
            <div className={`w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden ${heightClasses[height]}`}>
                <div 
                    className={`${fillColor} h-full rounded-full transition-all duration-500 ease-out`}
                    style={{ width: `${clampedProgress}%` }}
                    role="progressbar"
                    aria-valuenow={clampedProgress}
                    aria-valuemin={0}
                    aria-valuemax={100}
                />
            </div>
        </div>
    );
};
