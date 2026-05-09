// moe_llm_bench_grid.tsx — Interface Layer: LLM Bench Grid
// React TSX data grid mapping hardware benchmark JSON into a sortable table.

import React from 'react';

interface BenchResult {
  hardware: string;
  tps: number;
  memory_mb: number;
}

interface GridProps {
  data: BenchResult[];
}

export const BenchmarkGrid: React.FC<GridProps> = ({ data }) => {
  return React.createElement('table', { style: { width: '100%', borderCollapse: 'collapse' } },
    React.createElement('thead', null,
      React.createElement('tr', { style: { background: '#222', color: 'white' } },
        React.createElement('th', { style: { padding: '8px' } }, 'Hardware Platform'),
        React.createElement('th', { style: { padding: '8px' } }, 'Tokens/Sec'),
        React.createElement('th', { style: { padding: '8px' } }, 'VRAM Used (MB)')
      )
    ),
    React.createElement('tbody', null,
      data.map((row, idx) => 
        React.createElement('tr', { key: idx, style: { borderBottom: '1px solid #444' } },
          React.createElement('td', { style: { padding: '8px' } }, row.hardware),
          React.createElement('td', { style: { padding: '8px', color: '#00ff00' } }, row.tps.toFixed(2)),
          React.createElement('td', { style: { padding: '8px' } }, row.memory_mb)
        )
      )
    )
  );
};
