// Omni FLASK Skill Dashboard (TypeScript)
// Ref: kaistAI/FLASK — ICLR 2024
export interface SkillScore { name: string; score: number; }
export interface FlaskResult { model: string; skills: SkillScore[]; overall: number; }

export function evaluateModel(model: string, skills: SkillScore[]): FlaskResult {
  const valid = skills.filter(s => s.score >= 1 && s.score <= 5);
  const overall = valid.reduce((a, s) => a + s.score, 0) / Math.max(valid.length, 1);
  return { model, skills: valid, overall: Math.round(overall * 1e4) / 1e4 };
}

export function compareModels(results: FlaskResult[]): { winner: string; gap: number } {
  if (!results.length) return { winner: '', gap: 0 };
  const sorted = [...results].sort((a, b) => b.overall - a.overall);
  return { winner: sorted[0].model, gap: Math.round((sorted[0].overall - sorted[sorted.length-1].overall) * 1e4) / 1e4 };
}

export function radarChartData(result: FlaskResult): { labels: string[]; values: number[] } {
  return { labels: result.skills.map(s => s.name), values: result.skills.map(s => s.score) };
}
