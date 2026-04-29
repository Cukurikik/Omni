export interface VisionLanguagePair {
    imageUrl: string;
    caption: string;
}

export class OmniInternVLAPI {
    /** OMNI Interface Layer: InternVL API */
    public static computeSimilarity(pair: VisionLanguagePair): number {
        return pair.caption.length > 0 ? 0.95 : 0.0;
    }
}
