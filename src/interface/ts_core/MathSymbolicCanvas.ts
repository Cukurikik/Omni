export class MathSymbolicCanvas {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderExpression(expression: string, numericResult: number): void {
        this.container.innerHTML = `
            <div style="background: #f4f4f9; color: #333; padding: 20px; border-radius: 8px; font-family: 'Times New Roman', serif; border: 1px solid #ddd;">
                <div style="font-size: 24px; font-style: italic; border-bottom: 1px solid #ccc; padding-bottom: 10px; margin-bottom: 10px;">
                    $$ ${expression} $$
                </div>
                <div style="font-family: Inter, sans-serif; font-size: 16px;">
                    Numeric Evaluation: <strong>${numericResult.toPrecision(6)}</strong>
                </div>
            </div>
        `;
    }
}
