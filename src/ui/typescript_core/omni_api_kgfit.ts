export interface KGTriplet {
    head: string;
    relation: string;
    tail: string;
}

export class OmniKGFitAPI {
    /** OMNI Interface Layer: KG-FIT API */
    public static formatTripletPrompt(triplet: KGTriplet): string {
        return `[Fact]: ${triplet.head} is related to ${triplet.tail} via ${triplet.relation}.`;
    }

    public static validateTriplet(triplet: KGTriplet): boolean {
        return triplet.head !== '' && triplet.relation !== '' && triplet.tail !== '';
    }
}
