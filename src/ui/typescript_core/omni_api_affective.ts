export class OmniAffectiveAPI {
    public static arousal(gsr: number, hr: number, baseGsr: number, baseHr: number): number {
        const dGsr = (gsr - baseGsr) / (baseGsr || 1);
        const dHr = (hr - baseHr) / (baseHr || 1);
        return (dGsr + dHr) * 0.5;
    }
}
