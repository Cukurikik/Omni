using System;

namespace Omni.Domain.Compute
{
    public class CybertronMindsporeJob
    {
        public Guid JobId { get; }

        public CybertronMindsporeJob()
        {
            JobId = Guid.NewGuid();
        }
    }
}
