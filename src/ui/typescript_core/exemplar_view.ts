export interface Exemplar {
    id: number;
    score: number;
}
export function renderExemplars(ex: Exemplar[]): void {
    console.log("Rendering CEIL exemplars", ex);
}
