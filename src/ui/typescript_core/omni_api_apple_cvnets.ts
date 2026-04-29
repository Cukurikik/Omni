export class OmniAppleCVNetsAPI {
    public static gelu(x: number): number {
        return 0.5 * x * (1 + Math.tanh(0.7978846 * (x + 0.044715 * x ** 3)));
    }
}
