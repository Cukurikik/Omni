export class OmniADPapersAPI {
    public static citationImpact(citations: number, ageYears: number): number {
        return ageYears > 0 ? citations / Math.sqrt(ageYears) : citations;
    }
}
