export class OmniActionCLIPAPI {
    public static temporalPool(frames: number[][]): number[] {
        if (frames.length === 0) return [];
        const D = frames[0].length;
        const result = new Array(D).fill(0);
        for (const f of frames) for (let i = 0; i < D; ++i) result[i] += f[i];
        return result.map(v => v / frames.length);
    }
}
