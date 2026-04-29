import React, { useState, useMemo } from 'react';

// Strict typing for OMNI standards
export type MonadicResult<T, E> = { success: true; value: T } | { success: false; error: E };

export interface QuantumGate {
    id: string;
    type: 'H' | 'X' | 'Y' | 'Z' | 'CNOT';
    target: number;
    control?: number;
}

export const CircuitComposer: React.FC = () => {
    const [numQubits, setNumQubits] = useState<number>(3);
    const [gates, setGates] = useState<QuantumGate[]>([]);
    const [error, setError] = useState<string | null>(null);

    const addGate = (type: QuantumGate['type'], target: number, control?: number) => {
        if (target >= numQubits || (control !== undefined && control >= numQubits)) {
            setError('Qubit index out of bounds');
            return;
        }
        if (control !== undefined && control === target) {
            setError('Control and target cannot be the same');
            return;
        }

        const newGate: QuantumGate = {
            id: crypto.randomUUID(),
            type,
            target,
            control
        };
        setGates(prev => [...prev, newGate]);
        setError(null);
    };

    const clearCircuit = () => {
        setGates([]);
        setError(null);
    };

    const circuitMap = useMemo(() => {
        const map: string[][] = Array(numQubits).fill([]).map(() => []);
        gates.forEach(gate => {
            for (let q = 0; q < numQubits; q++) {
                if (q === gate.target) {
                    map[q].push(`[ ${gate.type} ]`);
                } else if (q === gate.control) {
                    map[q].push(`[ C ]`);
                } else {
                    map[q].push(`-----`);
                }
            }
        });
        return map;
    }, [gates, numQubits]);

    return (
        <div className="circuit-composer" style={{ padding: '20px', fontFamily: 'monospace' }}>
            <h2>OMNI Quantum Circuit Composer</h2>
            
            {error && <div style={{ color: 'red', marginBottom: '10px' }}>{error}</div>}
            
            <div className="controls" style={{ marginBottom: '20px' }}>
                <button onClick={() => addGate('H', 0)}>Add H to Q0</button>
                <button onClick={() => addGate('X', 1)}>Add X to Q1</button>
                <button onClick={() => addGate('CNOT', 1, 0)}>Add CNOT (C:0, T:1)</button>
                <button onClick={clearCircuit} style={{ marginLeft: '10px', color: 'red' }}>Clear</button>
            </div>

            <div className="circuit-grid" style={{ backgroundColor: '#1e1e1e', color: '#00ff00', padding: '20px', borderRadius: '5px' }}>
                {circuitMap.map((wire, qIdx) => (
                    <div key={qIdx} style={{ display: 'flex', alignItems: 'center', height: '40px' }}>
                        <div style={{ width: '40px', fontWeight: 'bold' }}>Q{qIdx}:</div>
                        <div>---</div>
                        {wire.map((sym, i) => (
                            <React.Fragment key={i}>
                                <div>{sym}</div>
                                <div>---</div>
                            </React.Fragment>
                        ))}
                    </div>
                ))}
                {gates.length === 0 && <div style={{ color: '#888' }}>Circuit is empty. Add gates to begin.</div>}
            </div>
        </div>
    );
};
