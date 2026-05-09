import React from 'react';

// OMNI MOTHER: App Header

export const OmniHeader: React.FC = () => {
    return (
        <header style={{ padding: '20px 0', borderBottom: '1px solid #334155', marginBottom: '30px' }}>
            <h1 style={{ margin: 0, color: '#3b82f6' }}>OMNI MOTHER</h1>
            <h2 style={{ margin: '5px 0 0 0', fontSize: '1.2rem', color: '#94a3b8' }}>Mixture-of-Experts Control Plane</h2>
        </header>
    );
};
