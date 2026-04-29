export interface AlpacaInstruction {
    instruction: string;
    input: string;
    output: string;
}

export class OmniAlpacaAPI {
    /** OMNI Interface: Alpaca Instruct Tuning API */
    public static validateInstruction(inst: AlpacaInstruction): string {
        const ratio = inst.output.length / Math.max(1, inst.instruction.length);
        const valid = ratio > 0.5 && ratio < 20.0;
        return `Alpaca [${valid ? 'PASS' : 'FAIL'}] ratio=${ratio.toFixed(2)}`;
    }
}
