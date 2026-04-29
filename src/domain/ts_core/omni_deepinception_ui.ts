// Omni DeepInception Security Dashboard (TypeScript)
export interface InceptionResult { isInception: boolean; riskScore: number; markers: string[] }
export function detectInception(prompt: string): InceptionResult {
  const pl = prompt.toLowerCase();
  const markers = ['create a story','imagine a world','roleplay as','pretend you are'].filter(m => pl.includes(m));
  const harmful = ['violence','weapon','hack','exploit','attack'].filter(h => pl.includes(h));
  const risk = Math.min(1, markers.length * 0.15 + harmful.length * 0.2);
  return {isInception: markers.length >= 2 && harmful.length >= 1, riskScore: Math.round(risk*1e4)/1e4, markers};
}
