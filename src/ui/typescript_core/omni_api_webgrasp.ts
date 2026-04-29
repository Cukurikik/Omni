export interface DOMElement {
    tag: string;
    id: string;
    xpath: string;
}

export class OmniWebGraspAPI {
    /** OMNI Interface Layer: WebGrasp API */
    public static generateLocator(element: DOMElement): string {
        if (element.id) {
            return `//*[@id="${element.id}"]`;
        }
        return element.xpath;
    }
}
