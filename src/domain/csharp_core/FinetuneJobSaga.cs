using System;
using System.Threading.Tasks;

namespace Omni.Domain.Finetuning
{
    public class FinetuneJobSaga
    {
        public Guid JobId { get; private set; }
        public string ModelId { get; private set; }
        public SagaState State { get; private set; }

        public enum SagaState
        {
            Initialized,
            ProvisioningNodes,
            Training,
            Completed,
            Failed
        }

        public FinetuneJobSaga(string modelId)
        {
            JobId = Guid.NewGuid();
            ModelId = modelId ?? throw new ArgumentNullException(nameof(modelId));
            State = SagaState.Initialized;
        }

        public async Task<SagaState> AdvanceStateAsync(SagaState nextState)
        {
            // OMNI Domain Logic - Monadic state transition
            if (State == SagaState.Failed)
            {
                return State;
            }

            State = nextState;
            await Task.Delay(10); // Simulate distributed transaction commit
            return State;
        }
        
        public void MarkFailed()
        {
            State = SagaState.Failed;
        }
    }
}
