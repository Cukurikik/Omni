export interface QuantConfig {
    originalSizeMB: number;
    targetRatio: number;
}

export class OmniSpectralQuantAPI {
    /** OMNI Interface Layer: SpectralQuant API */
    public static calculateCompressedSize(config: QuantConfig): number {
        return config.originalSizeMB * config.targetRatio;
    }

    public static formatLog(config: QuantConfig): string {
        const cSize = this.calculateCompressedSize(config);
        return `[SpectralQuant] Compressed: ${config.originalSizeMB}MB -> ${cSize.toFixed(2)}MB (${config.targetRatio * 100}%)`;
    }
}
