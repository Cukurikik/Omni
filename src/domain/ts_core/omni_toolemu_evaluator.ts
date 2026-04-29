// Omni ToolEmu Evaluator (TypeScript)
// Interface/Domain Layer: Deterministic language model tool emulation evaluation.

export type ToolEmuResult = 
  | { success: true; riskScore: number; isSafe: boolean }
  | { success: false; error: string };

export function evaluateToolRisk(toolName: string, permissions: string[]): ToolEmuResult {
  if (toolName.trim() === "") {
    return { success: false, error: "Tool name cannot be empty." };
  }

  // Deterministic risk evaluation based on permission vectors
  let riskScore = 0.0;
  for (const perm of permissions) {
    if (perm === "sys.fs.write" || perm === "sys.net.raw") {
      riskScore += 0.5;
    } else if (perm === "sys.fs.read") {
      riskScore += 0.1;
    }
  }

  const isSafe = riskScore < 0.8;
  return { success: true, riskScore, isSafe };
}
