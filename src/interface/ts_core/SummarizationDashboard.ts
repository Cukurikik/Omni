export class SummarizationDashboard {
    public displaySummary(text: string, elementId: string): void {
        if (!text) throw new Error("Summary text is empty");
        const el = document.getElementById(elementId);
        if (el) {
            el.innerText = text;
        }
    }
}
