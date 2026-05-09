using System;
using System.Threading.Tasks;

namespace Omni.Domain.GCP
{
    public class TpuProvisioningSaga
    {
        public string SagaId { get; private set; }
        public string TpuNodeName { get; private set; }
        public ProvisioningState State { get; private set; }

        public enum ProvisioningState
        {
            Started,
            ApiCalled,
            WaitingForReady,
            Completed,
            Failed
        }

        public TpuProvisioningSaga(string tpuNodeName)
        {
            SagaId = Guid.NewGuid().ToString();
            TpuNodeName = tpuNodeName;
            State = ProvisioningState.Started;
        }

        public async Task ExecuteStepAsync()
        {
            // OMNI Saga logic for state machine transitions
            if (State == ProvisioningState.Started)
            {
                State = ProvisioningState.ApiCalled;
                // Trigger GCP API call via Bridge
            }
            else if (State == ProvisioningState.ApiCalled)
            {
                State = ProvisioningState.WaitingForReady;
                // Setup polling
            }
            await Task.CompletedTask;
        }

        public void MarkCompleted()
        {
            State = ProvisioningState.Completed;
        }

        public void MarkFailed()
        {
            State = ProvisioningState.Failed;
        }
    }
}
