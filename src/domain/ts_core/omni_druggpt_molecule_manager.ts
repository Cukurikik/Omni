// Omni DrugGPT Molecule Manager (TypeScript)
// Domain: Protein-ligand pair registry.
// Ref: LIYUESEN/druggpt
interface LigandCandidate { smiles: string; mw: number; affinityScore: number; }
interface ProteinTarget { sequence: string; name: string; pdbId?: string; }
const targetRegistry = new Map<string, ProteinTarget>();
export function registerTarget(target: ProteinTarget): boolean {
  if (targetRegistry.has(target.name)) return false;
  targetRegistry.set(target.name, target);
  return true;
}
export function rankCandidates(candidates: LigandCandidate[]): LigandCandidate[] {
  return [...candidates].sort((a, b) => b.affinityScore - a.affinityScore);
}
