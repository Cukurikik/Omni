// Omni API for QuantumML Simulator
export interface QuantumCircuitLayer {
    layerIndex: number;
    gates: string[];
}

export class OmniQuantumMLAPI {
    static compileCircuitToJSON(layers: QuantumCircuitLayer[]): object {
        return {
            circuit_depth: layers.length,
            operations: layers.map(l => ({
                depth: l.layerIndex,
                gate_sequence: l.gates.join(',')
            }))
        };
    }
}
