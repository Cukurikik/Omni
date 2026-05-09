import React from 'react';

// OmniStatWidget.tsx — Dashboard Statistics Widget
// Layer: Interface / TypeScript
//
// A compact, highly-readable statistics card for top-level dashboard metrics.
// Includes strict typography and optional delta (trend) indicators.

export interface OmniStatWidgetProps {
    title: string;
    value: string | number;
    delta?: number; // Positive = up, negative = down
    deltaLabel?: string;
    icon?: React.ReactNode;
}

export const OmniStatWidget: React.FC<OmniStatWidgetProps> = ({
    title,
    value,
    delta,
    deltaLabel = "vs last week",
    icon
}) => {
    
    // Determine trend color and arrow
    let trendColor = "text-slate-500 dark:text-slate-400";
    let ArrowIcon = null;
    
    if (delta !== undefined) {
        if (delta > 0) {
            trendColor = "text-emerald-600 dark:text-emerald-400";
            ArrowIcon = () => (
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
            );
        } else if (delta < 0) {
            trendColor = "text-rose-600 dark:text-rose-400";
            ArrowIcon = () => (
                <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0v-8m0 8l-8-8-4 4-6-6" />
                </svg>
            );
        }
    }

    return (
        <div className="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-100 dark:border-slate-700 shadow-sm flex flex-col justify-between">
            <div className="flex justify-between items-start">
                <h4 className="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                    {title}
                </h4>
                {icon && (
                    <div className="p-2 bg-blue-50 dark:bg-slate-700/50 rounded-lg text-blue-600 dark:text-blue-400">
                        {icon}
                    </div>
                )}
            </div>
            
            <div className="mt-4">
                <span className="text-3xl font-bold text-slate-800 dark:text-slate-100 tracking-tight">
                    {value}
                </span>
            </div>
            
            {delta !== undefined && (
                <div className="mt-3 flex items-center text-sm">
                    <span className={`flex items-center font-semibold ${trendColor}`}>
                        {ArrowIcon && <ArrowIcon />}
                        {Math.abs(delta)}%
                    </span>
                    <span className="ml-2 text-slate-500 dark:text-slate-400">
                        {deltaLabel}
                    </span>
                </div>
            )}
        </div>
    );
};
