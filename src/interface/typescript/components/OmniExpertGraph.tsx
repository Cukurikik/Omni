import React from 'react';

// OMNI MOTHER: MoE Expert Activity Visualizer (Production Grade)

interface Expert {
    id: number;
    load: number; // 0 to 1
}

interface Props {
    experts: Expert[];
}

export const OmniExpertGraph: React.FC<Props> = ({ experts }) => {
    return (
        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {experts.map(ex => (
                <div 
                    key={ex.id}
                    style={{
                        width: '20px',
                        height: '20px',
                        backgroundColor: `rgba(255, 126, 179, ${ex.load})`,
                        border: '1px solid #FF7EB3',
                        borderRadius: '4px',
                        title: `Expert ${ex.id} Load: ${ex.load.toFixed(2)}`
                    }}
                />
            ))}
        </div>
    );
};
