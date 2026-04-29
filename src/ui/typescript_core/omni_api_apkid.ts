export interface APKScanResult {
    filename: string;
    packerDetected: boolean;
    entropy: number;
}

export class OmniAPKiDAPI {
    /** OMNI Interface: APKiD Scanner API */
    public static formatResult(result: APKScanResult): string {
        const status = result.packerDetected ? 'PACKED' : 'CLEAN';
        return `[APKiD] ${result.filename}: ${status} (entropy=${result.entropy.toFixed(3)})`;
    }
}
