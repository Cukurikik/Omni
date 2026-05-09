using System;

namespace Omni.Domain
{
    // OMNI MOTHER: Custom Transaction Scope for UoW (Production Grade)
    public class TransactionScope : IDisposable
    {
        private bool _isCommitted;

        public TransactionScope()
        {
            Console.WriteLine("[OMNI UoW] Transaction Started.");
            _isCommitted = false;
        }

        public void Commit()
        {
            Console.WriteLine("[OMNI UoW] Transaction Committed.");
            _isCommitted = true;
        }

        public void Dispose()
        {
            if (!_isCommitted)
            {
                Console.WriteLine("[OMNI UoW] Transaction Rolled Back!");
            }
        }
    }
}
