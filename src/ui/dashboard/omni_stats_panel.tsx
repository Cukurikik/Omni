// OmniStatsPanel.tsx — Reusable Dashboard Statistics Panel
// Layer: UI / TypeScript & React
//
// A high-density data visualization panel for the dashboard, rendering
// multiple key-value metrics with trend indicators.

import React from 'react';

interface Metric {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
}

interface OmniStatsPanelProps {
  title: string;
  metrics: Metric[];
}

export const OmniStatsPanel: React.FC<OmniStatsPanelProps> = ({ title, metrics }) => {
  return (
    <div className="omni-glass-panel">
      <h3 className="text-sm font-semibold text-gray-300 mb-4 uppercase tracking-wide">{title}</h3>
      
      <div className="grid grid-cols-2 gap-4">
        {metrics.map((metric, idx) => (
          <div key={idx} className="flex flex-col">
            <span className="text-xs text-gray-500 mb-1">{metric.label}</span>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold text-gray-100">{metric.value}</span>
              
              {metric.trend && metric.trendValue && (
                <span className={`text-xs font-medium flex items-center ${
                  metric.trend === 'up' ? 'text-green-400' : 
                  metric.trend === 'down' ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {metric.trend === 'up' && '↑'}
                  {metric.trend === 'down' && '↓'}
                  {metric.trend === 'neutral' && '→'}
                  <span className="ml-1">{metric.trendValue}</span>
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
