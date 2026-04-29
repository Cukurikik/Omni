// Omni DrugAssist Molecule Registry (TypeScript)
// Domain Layer: SMILES molecule registry and validation.
// Ref: blazerye/DrugAssist
interface MoleculeEntry { smiles: string; mw: number; logP: number; drugLikeness: boolean; }
const registry = new Map<string, MoleculeEntry>();
export function registerMolecule(entry: MoleculeEntry): boolean {
  if (registry.has(entry.smiles)) return false;
  registry.set(entry.smiles, entry);
  return true;
}
export function lookupMolecule(smiles: string): MoleculeEntry | undefined {
  return registry.get(smiles);
}
export function listDrugLike(): MoleculeEntry[] {
  return Array.from(registry.values()).filter(e => e.drugLikeness);
}
