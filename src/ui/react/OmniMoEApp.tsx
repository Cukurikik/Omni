import React from 'react';
import { OmniHeader } from './OmniHeader';
import { OmniFooter } from './OmniFooter';
import { OmniMoEVisualizer } from './OmniMoEVisualizer';
import { OmniExpertStats } from './OmniExpertStats';
import { OmniClusterMap } from './OmniClusterMap';

// OMNI MOTHER: Main App Composition

export const OmniMoEApp: React.FC = () => {
    return (
        <div className="omni-app-container">
            <OmniHeader />
            
            <OmniExpertStats 
                totalTokens={15420500} 
                imbalanceFactor={1.04} 
                avgLatency={12.4} 
            />
            
            <div style={{ display: 'flex', gap: '30px', flexWrap: 'wrap' }}>
                <div style={{ flex: '2 1 600px' }}>
                    <OmniMoEVisualizer />
                </div>
                <div style={{ flex: '1 1 300px' }}>
                    {/* Placeholder for map experts, would normally pass state down */}
                    <OmniClusterMap experts={[
                        { id: 'E-01', ipAddress: '', status: 'ONLINE', maxCapacity: 0, currentLoad: 0 },
                        { id: 'E-02', ipAddress: '', status: 'ONLINE', maxCapacity: 0, currentLoad: 0 },
                        { id: 'E-03', ipAddress: '', status: 'FAILED', maxCapacity: 0, currentLoad: 0 },
                        { id: 'E-04', ipAddress: '', status: 'ONLINE', maxCapacity: 0, currentLoad: 0 }
                    ]} />
                </div>
            </div>
            
            <OmniFooter />
        </div>
    );
};
