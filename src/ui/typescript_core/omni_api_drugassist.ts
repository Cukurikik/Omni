export class OmniDrugAssistAPI {
    /** OMNI Interface Layer: DrugAssist API */
    public static validateSMILESFormat(smiles: string): boolean {
        if (!smiles || smiles.length === 0) return false;
        const validChars = /^[CNOPSFIBrclH=\-\#\(\)\[\]\+]+$/;
        return validChars.test(smiles);
    }

    public static calculateComplexity(smiles: string): number {
        return smiles.length * (smiles.split('(').length);
    }
}
