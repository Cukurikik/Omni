// moe_tensorboard_plugin.ts — Interface / Analytics
// Layer: UI / Analytics — MoE Dashboard Components
//
// React components for visualizing MoE routing entropy, expert
// load balancing, and token dropping rates. Built for integration
// into the OMNI Admin dashboard.

import React, { useState, useEffect } from 'react';

// Interfaces for strict type safety
export interface ExpertMetrics {
  expertId: number;
  tokensProcessed: number;
  tokensDropped: number;
  averageComplexity: number;
  utilizationPercent: number;
}

export interface MoELayerStats {
  layerId: number;
  entropy: number;
  routingBalanceScore: number; // 0.0 to 1.0 (perfectly balanced)
  experts: ExpertMetrics[];
}

interface Props {
  layerData: MoELayerStats;
}

export const ExpertUtilizationHeatmap: React.FC<Props> = ({ layerData }) => {
  return (
    <div className="p-4 bg-gray-900 rounded-lg shadow-xl font-sans text-white">
      <h3 className="text-lg font-bold mb-4">
        Layer {layerData.layerId} Expert Utilization
      </h3>
      
      <div className="flex justify-between text-sm text-gray-400 mb-2">
        <span>Entropy: {layerData.entropy.toFixed(2)} nats</span>
        <span>Balance Score: {(layerData.routingBalanceScore * 100).toFixed(1)}%</span>
      </div>

      <div className="grid grid-cols-16 gap-1">
        {layerData.experts.map((expert) => {
          // Color coding based on utilization (red = overloaded/dropped, blue = underutilized, green = balanced)
          const heatLevel = expert.utilizationPercent;
          const dropRatio = expert.tokensDropped / Math.max(1, expert.tokensProcessed);
          
          let bgColor = 'bg-gray-700';
          if (dropRatio > 0.05) bgColor = 'bg-red-600';
          else if (heatLevel > 90) bgColor = 'bg-orange-500';
          else if (heatLevel > 50) bgColor = 'bg-green-500';
          else if (heatLevel > 10) bgColor = 'bg-blue-500';
          else bgColor = 'bg-blue-900';

          return (
            <div
              key={expert.expertId}
              className={`w-6 h-6 rounded-sm ${bgColor} hover:ring-2 hover:ring-white transition-all cursor-pointer`}
              title={`Expert ${expert.expertId}\nUtil: ${heatLevel.toFixed(1)}%\nDropped: ${expert.tokensDropped}`}
            />
          );
        })}
      </div>
      
      <div className="mt-4 flex items-center gap-4 text-xs text-gray-400">
        <span className="flex items-center gap-1"><div className="w-3 h-3 bg-blue-900 rounded-sm"></div> Idle</span>
        <span className="flex items-center gap-1"><div className="w-3 h-3 bg-green-500 rounded-sm"></div> Optimal</span>
        <span className="flex items-center gap-1"><div className="w-3 h-3 bg-red-600 rounded-sm"></div> Dropping</span>
      </div>
    </div>
  );
};
