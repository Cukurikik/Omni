using System;

namespace Omni.Business.BpfFirewall
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class VerifierRules
    {
        public OmniResult<bool> ValidateInstructionCount(int insn_count, bool has_loops)
        {
            if (insn_count <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Instruction count must be strictly positive"));
            }

            // eBPF strict verifier business logic
            // 1. Max 1,000,000 instructions in modern kernels
            if (insn_count > 1000000)
            {
                return new OmniResult<bool>(new InvalidOperationException("BPF program rejected: Exceeds 1M instruction complexity limit."));
            }

            // 2. Strict rejection of unbounded loops to prevent kernel lockups
            if (has_loops)
            {
                 // Modern BPF supports bounded loops, but for strict zero-mock firewall validation we reject
                 return new OmniResult<bool>(new InvalidOperationException("BPF program rejected: Unbounded loops are not permitted in kernel space."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
