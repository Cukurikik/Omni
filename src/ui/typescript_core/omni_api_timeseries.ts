export interface TimeSeriesResult {
    trend: number[];
    seasonal: number[];
}

export class OmniTimeSeriesAPI {
    /** OMNI Interface Layer: TimeSeries API */
    public static computeMovingAverage(data: number[], window: number): number[] {
        if (window <= 0) return data;
        let result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - window + 1);
            const slice = data.slice(start, i + 1);
            result.push(slice.reduce((a, b) => a + b, 0) / slice.length);
        }
        return result;
    }
}
