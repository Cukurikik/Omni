export class OmniAlbumentationsAPI {
    public static normalize(pixels: number[], mean: number, std: number): number[] {
        return pixels.map(p => (p - mean) / std);
    }
}
