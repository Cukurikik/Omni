import React from 'react';
import { ExpertNode } from '../typescript/omni_moe_dashboard';

// OMNI MOTHER: React component for a topological cluster map

interface Props {
    experts: ExpertNode[];
}

export const OmniClusterMap: React.FC<Props> = ({ experts }) => {
    // Simple ring topology visualization logic
    const radius = 150;
    const center = { x: 200, y: 200 };

    return (
        <div className="omni-cluster-map">
            <h3>Topological Map</h3>
            <svg width="400" height="400">
                {/* Draw connection ring */}
                <circle cx={center.x} cy={center.y} r={radius} fill="none" stroke="#334155" strokeWidth="2" />
                
                {experts.map((exp, i) => {
                    const angle = (i / experts.length) * 2 * Math.PI - Math.PI / 2;
                    const x = center.x + radius * Math.cos(angle);
                    const y = center.y + radius * Math.sin(angle);
                    
                    const color = exp.status === 'ONLINE' ? '#10b981' : 
                                  exp.status === 'FAILED' ? '#ef4444' : '#f59e0b';

                    return (
                        <g key={exp.id}>
                            <circle cx={x} cy={y} r="15" fill={color} />
                            <text x={x} y={y + 30} fill="#e2e8f0" fontSize="12" textAnchor="middle">
                                {exp.id}
                            </text>
                        </g>
                    );
                })}
            </svg>
        </div>
    );
};
