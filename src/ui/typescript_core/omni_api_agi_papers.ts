export class OmniAGIPapersAPI {
    public static noveltyScore(refs: number, selfCites: number, totalRefs: number): number {
        if (totalRefs <= 0) return 0;
        return Math.max(0, (refs - selfCites) / totalRefs);
    }
}
