export interface BEVObject {
    label: string;
    x: number;
    y: number;
}

export class OmniTalk2BEVAPI {
    /** OMNI Interface Layer: Talk2BEV API */
    public static serializeState(objects: BEVObject[]): string {
        return JSON.stringify(objects);
    }
}
