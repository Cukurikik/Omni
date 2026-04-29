// Omni API for LLM4Regression
export interface RegressionResult {
    inputs: number[];
    actuals: number[];
    predictions: number[];
}

export class OmniLLM4RegressionAPI {
    static generateChartPayload(result: RegressionResult): object {
        const dataPoints = result.inputs.map((x, i) => ({
            x: x,
            actual: result.actuals[i],
            predicted: result.predictions[i]
        }));
        
        return {
            chartType: "scatter_line",
            dataset: dataPoints.sort((a, b) => a.x - b.x)
        };
    }
}
