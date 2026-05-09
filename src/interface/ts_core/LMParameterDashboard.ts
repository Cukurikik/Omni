export interface LMTrainingStats {
    epoch: number;
    step: number;
    loss: number;
    learningRate: number;
    tokensPerSec: number;
}

export class LMParameterDashboard {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public updateStats(stats: LMTrainingStats): void {
        this.container.innerHTML = `
            <div style="background: #1e1e1e; color: #00ffaa; padding: 20px; font-family: monospace; border-radius: 8px;">
                <h3>LM Training Telemetry</h3>
                <p>Epoch: <strong>${stats.epoch}</strong></p>
                <p>Step: <strong>${stats.step}</strong></p>
                <p>Loss: <strong>${stats.loss.toFixed(4)}</strong></p>
                <p>LR: <strong>${stats.learningRate.toExponential(2)}</strong></p>
                <p>Throughput: <strong>${stats.tokensPerSec.toFixed(0)} tok/s</strong></p>
            </div>
        `;
    }
}
