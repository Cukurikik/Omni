import React from 'react';

// OmniChartTooltip.tsx — Chart Hover Tooltip
// Layer: Interface / TypeScript
//
// A reusable, accessible tooltip component designed to float over data points
// on Recharts or Chart.js visualizations within the OMNI Dashboard.

export interface TooltipItem {
    name: string;
    value: string | number;
    color?: string;
}

export interface OmniChartTooltipProps {
    active?: boolean;
    payload?: Array<{
        name: string;
        value: number;
        color: string;
        payload: any;
    }>;
    label?: string;
    valueFormatter?: (value: number) => string;
}

export const OmniChartTooltip: React.FC<OmniChartTooltipProps> = ({
    active,
    payload,
    label,
    valueFormatter = (val) => val.toString()
}) => {
    
    if (!active || !payload || payload.length === 0) {
        return null;
    }

    return (
        <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-md border border-slate-200 dark:border-slate-700 shadow-lg rounded-lg p-3 text-sm focus:outline-none pointer-events-none z-50">
            {label && (
                <div className="font-semibold text-slate-800 dark:text-slate-100 mb-2 border-b border-slate-100 dark:border-slate-700 pb-1">
                    {label}
                </div>
            )}
            <div className="space-y-1.5">
                {payload.map((entry, index) => (
                    <div key={`item-${index}`} className="flex items-center justify-between space-x-4">
                        <div className="flex items-center space-x-2">
                            <span 
                                className="w-2.5 h-2.5 rounded-full flex-shrink-0" 
                                style={{ backgroundColor: entry.color || '#3b82f6' }}
                            />
                            <span className="text-slate-600 dark:text-slate-300 font-medium capitalize">
                                {entry.name}
                            </span>
                        </div>
                        <span className="text-slate-800 dark:text-slate-100 font-bold tabular-nums">
                            {valueFormatter(entry.value)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};
