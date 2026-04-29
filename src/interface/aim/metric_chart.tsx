import React from 'react';

// Purely mathematical rendering for the chart
export const MetricChart = ({ metricName, data }: { metricName: string, data: number[][] }) => {
    // Generate SVG path points
    const drawLine = (pts: number[]) => {
        const maxVal = Math.max(...pts, 1);
        return pts.map((v, i) => `${i * 10},${100 - (v / maxVal * 100)}`).join(' L ');
    };

    return (
        <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px' }}>
            <h4>{metricName}</h4>
            <svg width="100%" height="150" viewBox="0 0 300 100" preserveAspectRatio="none">
                {data.map((pts, idx) => (
                    <path 
                        key={idx}
                        d={`M ${drawLine(pts)}`} 
                        fill="none" 
                        stroke={`hsl(${idx * 137 % 360}, 70%, 50%)`} 
                        strokeWidth="2" 
                    />
                ))}
            </svg>
        </div>
    );
};
