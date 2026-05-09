using System;

namespace Omni.Domain.Vision
{
    public class SelfReformerProcess
    {
        public Guid ProcessId { get; }

        public SelfReformerProcess()
        {
            ProcessId = Guid.NewGuid();
        }
    }
}
