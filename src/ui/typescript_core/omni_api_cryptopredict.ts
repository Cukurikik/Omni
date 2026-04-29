// Omni API for CryptoPredict Time-Series
export interface CryptoForecast {
    assetSymbol: string;
    currentPrice: number;
    predictedPrice24h: number;
}

export class OmniCryptoPredictAPI {
    static evaluateSignal(forecast: CryptoForecast): "BUY" | "SELL" | "HOLD" {
        const delta = (forecast.predictedPrice24h - forecast.currentPrice) / forecast.currentPrice;
        if (delta > 0.05) return "BUY";
        if (delta < -0.05) return "SELL";
        return "HOLD";
    }
}
