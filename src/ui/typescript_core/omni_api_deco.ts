export interface DecoConfig {
    threshold: number;
    penalty: number;
    temperature: number;
}

export class OmniDecoAPI {
    /** OMNI Interface Layer: Deco Decoding API */
    public static validateConfig(config: DecoConfig): boolean {
        return config.temperature > 0 && config.penalty >= 0 && config.threshold > 0;
    }

    public static createDefaultConfig(): DecoConfig {
        return {
            threshold: 0.8,
            penalty: 1.5,
            temperature: 0.7
        };
    }
}
