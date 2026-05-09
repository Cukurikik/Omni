using System;

namespace Omni.Domain.Evaluation
{
    public class NapolabTestRun
    {
        public Guid RunId { get; }

        public NapolabTestRun()
        {
            RunId = Guid.NewGuid();
        }
    }
}
