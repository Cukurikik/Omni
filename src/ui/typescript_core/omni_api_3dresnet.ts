export class Omni3DResNetAPI {
    public static avgPool(volume: number[]): number {
        if (volume.length === 0) return 0;
        return volume.reduce((s, v) => s + v, 0) / volume.length;
    }
}
