import React, { useState } from 'react';

export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

interface LayerNode {
    id: string;
    type: string;
    units: number;
}

export const ModelVisualizer: React.FC = () => {
    const [layers, setLayers] = useState<LayerNode[]>([]);
    const [unitsInput, setUnitsInput] = useState<number>(64);
    const [typeInput, setTypeInput] = useState<string>('Dense');
    const [error, setError] = useState<string | null>(null);

    const handleAddLayer = () => {
        if (unitsInput <= 0) {
            setError("Units must be positive.");
            return;
        }
        setError(null);
        setLayers([...layers, { id: crypto.randomUUID(), type: typeInput, units: unitsInput }]);
    };

    const handleClear = () => {
        setLayers([]);
        setError(null);
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif', backgroundColor: '#1e1e1e', color: '#d4d4d4', minHeight: '100vh' }}>
            <h1 style={{ color: '#569cd6' }}>OMNI Haiku Network Visualizer</h1>
            
            <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#2d2d2d', borderRadius: '8px' }}>
                <select value={typeInput} onChange={e => setTypeInput(e.target.value)} style={{ marginRight: '10px', padding: '5px' }}>
                    <option value="Dense">Dense</option>
                    <option value="Conv2D">Conv2D</option>
                    <option value="MaxPool">MaxPool</option>
                </select>
                <input 
                    type="number" 
                    value={unitsInput} 
                    onChange={e => setUnitsInput(Number(e.target.value))} 
                    placeholder="Units/Filters"
                    style={{ marginRight: '10px', padding: '5px', width: '100px' }}
                />
                <button onClick={handleAddLayer} style={{ padding: '6px 12px', backgroundColor: '#007acc', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}>
                    Add Layer
                </button>
                <button onClick={handleClear} style={{ marginLeft: '10px', padding: '6px 12px', backgroundColor: '#c53b3b', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}>
                    Clear
                </button>
            </div>

            {error && <div style={{ color: '#f48771', marginBottom: '10px' }}>{error}</div>}

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' }}>
                {layers.length === 0 && <div style={{ color: '#808080' }}>No layers defined. Add layers to visualize.</div>}
                {layers.map((layer, index) => (
                    <React.Fragment key={layer.id}>
                        <div style={{ 
                            padding: '15px 30px', 
                            backgroundColor: layer.type === 'Dense' ? '#4CAF50' : '#2196F3', 
                            color: 'white', 
                            borderRadius: '8px',
                            minWidth: '200px',
                            textAlign: 'center',
                            boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
                        }}>
                            <div style={{ fontWeight: 'bold' }}>{layer.type}</div>
                            <div>{layer.units} units/filters</div>
                        </div>
                        {index < layers.length - 1 && (
                            <div style={{ height: '30px', width: '2px', backgroundColor: '#555' }}></div>
                        )}
                    </React.Fragment>
                ))}
            </div>
        </div>
    );
};
