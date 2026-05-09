using System.Collections.Generic;

namespace OmniMoE.Domain
{
    // OMNI MOTHER: C# MoE Orchestrator
    
    public class OmniMoEOrchestrator
    {
        private List<string> activeExperts = new List<string>();

        public void RegisterExpert(string id)
        {
            if (!activeExperts.Contains(id))
            {
                activeExperts.Add(id);
                System.Console.WriteLine($"[OMNI] Expert Registered: {id}");
            }
        }
    }
}
