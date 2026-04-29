export interface EditRequest {
    subject: string;
    newFact: string;
}

export class OmniAwesomeKEAPI {
    /** OMNI Interface Layer: Awesome-KE API */
    public static initiateEdit(req: EditRequest): string {
        return `Initiating knowledge edit on ${req.subject} -> ${req.newFact}`;
    }
}
