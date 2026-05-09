// moe_longshu_game_state.cs — Domain
// Layer: Domain — LongShu Game State Management
// Inspired by: LongShuGameDev (A Game Development LLM)

using System;
using System.Collections.Generic;

namespace Omni.Domain.MoE
{
    public class GameStateContext
    {
        public string EngineTarget { get; private set; }
        public Dictionary<string, string> ActiveScripts { get; private set; }
        public List<string> CompilationErrors { get; private set; }

        public GameStateContext(string engineTarget)
        {
            if (engineTarget != "Unity" && engineTarget != "Unreal")
            {
                throw new ArgumentException("Engine target must be 'Unity' or 'Unreal'");
            }
            EngineTarget = engineTarget;
            ActiveScripts = new Dictionary<string, string>();
            CompilationErrors = new List<string>();
        }

        public void UpdateScript(string className, string code)
        {
            // Domain Rule: Unity requires MonoBehaviour
            if (EngineTarget == "Unity" && !code.Contains("MonoBehaviour"))
            {
                CompilationErrors.Add($"[{className}] Missing MonoBehaviour inheritance.");
            }
            
            // Domain Rule: Unreal requires UCLASS
            if (EngineTarget == "Unreal" && !code.Contains("UCLASS()"))
            {
                CompilationErrors.Add($"[{className}] Missing UCLASS() macro.");
            }

            ActiveScripts[className] = code;
        }

        public bool IsStateValid()
        {
            return CompilationErrors.Count == 0;
        }
    }
}
