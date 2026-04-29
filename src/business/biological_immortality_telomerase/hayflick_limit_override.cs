using System;

namespace Omni.Business.BiologicalImmortalityTelomerase
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HayflickLimitOverride
    {
        public OmniResult<string> EvaluateCancerRisk(double telomerase_activity_factor, int detected_mutations)
        {
            if (telomerase_activity_factor < 0 || detected_mutations < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid somatic metrics"));
            }

            // Bio-Engineering Business Logic: Somatic Immortality vs Oncology
            // Activating telomerase in somatic (body) cells makes them immortal, effectively curing aging.
            // HOWEVER, if a cell accumulates DNA mutations and becomes cancerous, the telomerase will
            // also make the cancer immortal (malignant metastasis).
            // We must strictly throttle telomerase if mutations are detected.
            
            if (telomerase_activity_factor > 0.8 && detected_mutations > 5)
            {
                return new OmniResult<string>("ONCOLOGICAL_THREAT_DETECTED: Immortalizing mutated cells will cause malignant carcinoma. Halting nanobody transcriptase injection.");
            }
            
            return new OmniResult<string>("CELLULAR_REJUVENATION_ACTIVE: Telomeres extending. Senescence reversed. Bio-markers indicating youthful phenotype.");
        }
    }
}
