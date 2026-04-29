export interface GenomicSequence {
    id: string;
    seq: string;
}

export class OmniGenomeAPI {
    /** OMNI Interface Layer: Genome Factory API */
    public static calculateLength(seq: GenomicSequence): number {
        return seq.seq.length;
    }
}
