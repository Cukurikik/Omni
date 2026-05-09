//=============================================================================
// OMNI DOMAIN LAYER — MRI PATIENT MODELS (C#)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: DDD aggregates for SLATER MRI Reconstructions.
// INSPIRED BY: icon-lab/SLATER
//=============================================================================

using System;
using OmniBridge.Domain.Types;

namespace Omni.Domain.Medical
{
    // OMNI IDIOM: Aggregate Root for Patient Medical Data
    public class MriPatientRecord
    {
        public string PatientId { get; private set; }
        public DateTime DateOfScan { get; private set; }
        public ReconstructionStatus Status { get; private set; }
        public string ArtifactStorageUrl { get; private set; }

        public MriPatientRecord(string patientId)
        {
            PatientId = patientId;
            DateOfScan = DateTime.UtcNow;
            Status = ReconstructionStatus.Queued;
        }

        public MonadicResult<bool> MarkProcessing()
        {
            if (Status != ReconstructionStatus.Queued)
            {
                return MonadicResult<bool>.Fail("Record is not in queued state.");
            }
            
            Status = ReconstructionStatus.Processing;
            return MonadicResult<bool>.Ok(true);
        }

        public MonadicResult<bool> CompleteReconstruction(string artifactUrl)
        {
            if (Status != ReconstructionStatus.Processing)
            {
                return MonadicResult<bool>.Fail("Record must be processing to complete.");
            }

            if (string.IsNullOrWhiteSpace(artifactUrl))
            {
                return MonadicResult<bool>.Fail("Artifact URL cannot be empty.");
            }

            Status = ReconstructionStatus.Completed;
            ArtifactStorageUrl = artifactUrl;
            return MonadicResult<bool>.Ok(true);
        }
    }

    public enum ReconstructionStatus
    {
        Queued,
        Processing,
        Completed,
        Failed
    }
}
