export class OmniAdEMAMixAPI {
    public static step(grad: number, m1: number, m2: number, b1: number, b2: number, a: number): number {
        const nm1 = b1 * m1 + (1 - b1) * grad;
        const nm2 = b2 * m2 + (1 - b2) * grad;
        return a * nm1 + (1 - a) * nm2;
    }
}
