export interface CPMConfig {
    quantization: string;
    sparsity: number;
}

export class OmniMiniCPMAPI {
    /** OMNI Interface Layer: MiniCPM API */
    public static initialize(config: CPMConfig): string {
        return `MiniCPM Init: ${config.quantization} @ ${config.sparsity}% sparse`;
    }
}
