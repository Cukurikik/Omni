// moe_perft_state.cs — Domain Layer: PERFT State
// C# entity tracking Parameter-Efficient Fine-Tuning adapter lifecycles.

using System;

namespace Omni.Domain.MoE.Perft
{
    public class AdapterState
    {
        public string AdapterId { get; private set; }
        public AdapterStatus Status { get; private set; }
        public DateTime LastActivated { get; private set; }

        public AdapterState(string id)
        {
            AdapterId = id;
            Status = AdapterStatus.Inactive;
            LastActivated = DateTime.MinValue;
        }

        public void Activate()
        {
            Status = AdapterStatus.Active;
            LastActivated = DateTime.UtcNow;
        }

        public void Deactivate()
        {
            Status = AdapterStatus.Inactive;
        }
    }

    public enum AdapterStatus
    {
        Inactive,
        Loading,
        Active,
        Faulted
    }
}
