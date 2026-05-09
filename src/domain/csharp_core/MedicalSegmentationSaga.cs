using System;

namespace Omni.Domain.Medical
{
    public class MedicalSegmentationSaga
    {
        public Guid SagaId { get; private set; }
        public string Status { get; private set; }

        public MedicalSegmentationSaga()
        {
            SagaId = Guid.NewGuid();
            Status = "Initialized";
        }

        public void ProcessScan(byte[] scanData)
        {
            if (scanData == null || scanData.Length == 0)
                throw new ArgumentException("Scan data cannot be empty");
            
            Status = "Processing";
        }

        public void Complete()
        {
            Status = "Completed";
        }
    }
}
