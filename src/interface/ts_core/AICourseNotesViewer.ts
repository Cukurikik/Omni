export class AICourseNotesViewer {
    public renderNotes(content: string, elementId: string): void {
        const el = document.getElementById(elementId);
        if (el) {
            el.innerHTML = `<div>${content}</div>`;
        }
    }
}
