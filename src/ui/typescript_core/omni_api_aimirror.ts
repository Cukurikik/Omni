export class OmniAIMirrorAPI {
    public static featureDistance(src: number[], tgt: number[]): number {
        let sum = 0;
        for (let i = 0; i < src.length; ++i) sum += (src[i] - tgt[i]) ** 2;
        return Math.sqrt(sum);
    }
}
