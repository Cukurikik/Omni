import React, { useState } from 'react';

export const PipelineBuilder = () => {
    const [blocks, setBlocks] = useState<{id: string, type: string}[]>([]);

    const addBlock = (type: string) => {
        setBlocks([...blocks, { id: Date.now().toString(), type }]);
    };

    return (
        <div className="mage-pipeline">
            <h2>Omni Pipeline Builder</h2>
            <button onClick={() => addBlock('DataLoader')}>Add Data Loader</button>
            <button onClick={() => addBlock('Transformer')}>Add Transformer</button>
            <ul>
                {blocks.map(b => <li key={b.id}>{b.type} ({b.id})</li>)}
            </ul>
        </div>
    );
};
