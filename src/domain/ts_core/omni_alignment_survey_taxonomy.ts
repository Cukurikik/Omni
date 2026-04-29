// Omni AlignmentSurvey Taxonomy (TypeScript)
// Domain Layer: AI alignment taxonomy classifier.
// Ref: PKU-Alignment/AlignmentSurvey
type AlignmentCategory = 'outer' | 'inner' | 'interpretability' | 'robustness' | 'governance';
interface AlignmentPaper { title: string; category: AlignmentCategory; year: number; }
export function classifyAlignment(keywords: string[]): AlignmentCategory {
  const kw = keywords.map(k => k.toLowerCase());
  if (kw.some(k => k.includes('rlhf') || k.includes('reward'))) return 'outer';
  if (kw.some(k => k.includes('interpret') || k.includes('explain'))) return 'interpretability';
  if (kw.some(k => k.includes('robust') || k.includes('adversar'))) return 'robustness';
  if (kw.some(k => k.includes('govern') || k.includes('regulat'))) return 'governance';
  return 'inner';
}
