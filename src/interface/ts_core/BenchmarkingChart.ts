export class BenchmarkingChart {
    public renderChart(accuracy: number, containerId: string): void {
        const el = document.getElementById(containerId);
        if (el) {
            el.innerHTML = `<div>Accuracy: ${(accuracy * 100).toFixed(2)}%</div>`;
        }
    }
}
