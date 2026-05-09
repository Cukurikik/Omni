//=============================================================================
// OMNI DOMAIN LAYER — MRI VALIDATOR (C#)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: C# DDD logic for validating K-Space data structures before 
//              they enter the compute reconstruction pipeline.
//=============================================================================

using System;
using OmniBridge.Domain.Types;

namespace Omni.Domain.Medical
{
    public class MriValidator
    {
        // OMNI IDIOM: Monadic validation
        public MonadicResult<bool> ValidateKSpaceMetadata(KSpaceMetadata meta)
        {
            if (meta == null)
            {
                return MonadicResult<bool>.Fail("Metadata cannot be null.");
            }

            if (meta.ResolutionX <= 0 || meta.ResolutionY <= 0)
            {
                return MonadicResult<bool>.Fail("Invalid spatial resolution dimensions.");
            }

            if (meta.UndersamplingFactor < 1.0f || meta.UndersamplingFactor > 10.0f)
            {
                return MonadicResult<bool>.Fail("Undersampling factor is out of acceptable clinical bounds (1x-10x).");
            }

            if (string.IsNullOrWhiteSpace(meta.MachineId))
            {
                return MonadicResult<bool>.Fail("MRI Machine ID is required for calibration offset lookup.");
            }

            return MonadicResult<bool>.Ok(true);
        }
    }

    public class KSpaceMetadata
    {
        public int ResolutionX { get; set; }
        public int ResolutionY { get; set; }
        public float UndersamplingFactor { get; set; }
        public string MachineId { get; set; }
    }
}
