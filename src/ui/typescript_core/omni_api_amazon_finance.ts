export class OmniAmazonFinanceAPI {
    public static bollingerBands(sma: number, stdDev: number, k = 2): {upper: number; lower: number} {
        return { upper: sma + k * stdDev, lower: sma - k * stdDev };
    }
    public static ema(price: number, prevEma: number, alpha: number): number {
        return alpha * price + (1 - alpha) * prevEma;
    }
}
