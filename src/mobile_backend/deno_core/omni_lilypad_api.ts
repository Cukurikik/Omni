// Omni Lilypad Version API (Deno)
// Ref: Mirascope/lilypad
const versions = new Map();

export function hashPrompt(template, vars) {
  let h = 0;
  const s = template + JSON.stringify(vars);
  for (let i = 0; i < s.length; i++) { h = ((h << 5) - h + s.charCodeAt(i)) | 0; }
  return Math.abs(h).toString(16).padStart(8, '0');
}

export function createVersion(template, variables) {
  const hash = hashPrompt(template, variables);
  const v = { hash, template, variables, createdAt: Date.now() };
  versions.set(hash, v);
  return v;
}

export function getVersion(hash) { return versions.get(hash) || null; }

export function listVersions() { return Array.from(versions.values()); }
