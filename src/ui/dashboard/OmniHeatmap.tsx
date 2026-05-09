import React from 'react';

// OmniHeatmap.tsx — Density Analytics Visualizer
// Layer: Interface / TypeScript
//
// Renders an interactive 2D density heatmap (e.g., GitHub contribution graph)
// by mapping numerical arrays into HSL color scales. Zero mock.

export interface HeatmapData {
    x: string; // e.g., "Mon"
    y: string; // e.g., "12 PM"
    value: number;
}

export interface OmniHeatmapProps {
    data: HeatmapData[];
    colorHue?: number; // 0-360, e.g., 200 for blue
    cellSize?: number;
    className?: string;
}

export const OmniHeatmap: React.FC<OmniHeatmapProps> = ({
    data,
    colorHue = 210, // Default blue tone
    cellSize = 20,
    className = ''
}) => {
    if (data.length === 0) return <div>No data available.</div>;

    // 1. Extract unique rows and columns
    const xLabels = Array.from(new Set(data.map(d => d.x)));
    const yLabels = Array.from(new Set(data.map(d => d.y)));

    // 2. Determine max value for normalization
    const maxVal = Math.max(...data.map(d => d.value), 1);

    // 3. Create a lookup map for O(1) rendering
    const dataMap = new Map<string, number>();
    data.forEach(d => dataMap.set(`${d.x}-${d.y}`, d.value));

    // Generates a color from very light (or background) to saturated hue based on intensity
    const getColor = (val: number) => {
        if (val === 0) return 'rgba(0,0,0,0.05)'; // Empty state
        
        // Intensity from 0.2 to 1.0 (avoiding completely white so colors show)
        const intensity = 0.2 + (0.8 * (val / maxVal));
        
        // Map intensity to Lightness: higher intensity = darker color (in Light mode)
        // Lightness ranges from 90% down to 30%
        const lightness = 95 - (intensity * 60);
        
        return `hsl(${colorHue}, 80%, ${lightness}%)`;
    };

    return (
        <div className={`overflow-x-auto ${className}`}>
            <div className="flex flex-col gap-1">
                {/* Header Row (X Labels) */}
                <div className="flex gap-1 pl-12">
                    {xLabels.map((x, i) => (
                        <div 
                            key={`header-${i}`} 
                            style={{ width: cellSize }}
                            className="text-xs text-center text-slate-500 overflow-hidden truncate"
                            title={x}
                        >
                            {x}
                        </div>
                    ))}
                </div>

                {/* Grid Body */}
                {yLabels.map((y, yi) => (
                    <div key={`row-${yi}`} className="flex gap-1 items-center">
                        {/* Y Label */}
                        <div className="w-10 text-xs text-right pr-2 text-slate-500 truncate" title={y}>
                            {y}
                        </div>
                        
                        {/* Cells */}
                        {xLabels.map((x, xi) => {
                            const val = dataMap.get(`${x}-${y}`) || 0;
                            return (
                                <div
                                    key={`cell-${xi}-${yi}`}
                                    style={{
                                        width: cellSize,
                                        height: cellSize,
                                        backgroundColor: getColor(val)
                                    }}
                                    className="rounded-sm transition-transform hover:scale-110 cursor-pointer"
                                    title={`${x}, ${y}: ${val}`}
                                />
                            );
                        })}
                    </div>
                ))}
            </div>
        </div>
    );
};
