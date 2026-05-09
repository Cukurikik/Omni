import React, { useEffect, useState } from 'react';
import { OmniMoEDashboardClient, ExpertNode } from '../typescript/omni_moe_dashboard';

// OMNI MOTHER: React component for visualising expert load.

const client = new OmniMoEDashboardClient();

export const OmniMoEVisualizer: React.FC = () => {
    const [experts, setExperts] = useState<ExpertNode[]>([]);

    useEffect(() => {
        const loadData = async () => {
            const data = await client.fetchExperts();
            setExperts(data);
        };
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="omni-moe-visualizer">
            <h2>OMNI MoE Cluster Status</h2>
            <div className="expert-grid">
                {experts.map(expert => {
                    const loadPercentage = (expert.currentLoad / expert.maxCapacity) * 100;
                    let statusClass = 'expert-card ' + expert.status.toLowerCase();
                    
                    return (
                        <div key={expert.id} className={statusClass}>
                            <h3>{expert.id}</h3>
                            <p>IP: {expert.ipAddress}</p>
                            <p>Status: <strong>{expert.status}</strong></p>
                            <div className="load-bar-container">
                                <div 
                                    className="load-bar" 
                                    style={{ width: `${loadPercentage}%`, backgroundColor: loadPercentage > 85 ? 'red' : 'green' }}
                                ></div>
                            </div>
                            <p className="load-text">{expert.currentLoad} / {expert.maxCapacity} tokens</p>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
