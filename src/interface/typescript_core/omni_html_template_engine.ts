// OMNI Interface Layer: HTML Semantic Template Generator
export class OmniHtmlEngine {
    public generate(data: any): string {
        return `<div id="omni-root" data-state="${data}"></div>`;
    }
}
