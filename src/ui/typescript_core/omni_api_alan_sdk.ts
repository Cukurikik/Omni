export class OmniAlanSDKAPI {
    public static vadEnergy(samples: number[]): number {
        if (samples.length === 0) return 0;
        const rms = samples.reduce((s, v) => s + v * v, 0) / samples.length;
        return Math.sqrt(rms);
    }
}
