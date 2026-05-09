import React from 'react';

// OMNI MOTHER: SVG Metrics Chart Component (Production Grade)
// Zero-dependency sparkline chart for monitoring GPU loads.

interface Props {
    data: number[];
    color?: string;
}

export const OmniMetricsChart: React.FC<Props> = ({ data, color = "#FF7EB3" }) => {
    if (!data || data.length === 0) return <div>No Data</div>;

    const max = Math.max(...data, 100);
    const min = Math.min(...data, 0);
    const range = max - min || 1;

    const points = data.map((val, idx) => {
        const x = (idx / (data.length - 1)) * 100;
        const y = 100 - ((val - min) / range) * 100;
        return `${x},${y}`;
    }).join(' ');

    return (
        <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none">
            <polyline 
                fill="none" 
                stroke={color} 
                strokeWidth="2" 
                points={points} 
                vectorEffect="non-scaling-stroke" 
            />
        </svg>
    );
};
