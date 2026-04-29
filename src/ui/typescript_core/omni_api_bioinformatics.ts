// Omni API for BioInformatics Sequencing
export interface SequenceAlignment {
    seqA: string;
    seqB: string;
    score: number;
}

export class OmniBioInformaticsAPI {
    static formatAlignmentView(alignment: SequenceAlignment): string {
        return `Seq1: ${alignment.seqA}\nSeq2: ${alignment.seqB}\nScore: ${alignment.score}`;
    }
}
