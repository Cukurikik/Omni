using System;

namespace Omni.Domain.AI
{
    public class LLMFromScratchOrchestrator
    {
        public bool IsReady { get; private set; }

        public void Initialize()
        {
            IsReady = true;
        }
    }
}
