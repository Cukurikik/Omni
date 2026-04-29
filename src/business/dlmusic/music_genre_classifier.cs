using System;
using Omni.Core.Result;

namespace Omni.Business.DLMusic
{
    // OMNI BUSINESS LAYER: DL Music
    // Genre classification business rules based on feature metrics.

    public class MusicGenreClassifier
    {
        public OmniResult<string, string> ClassifyGenre(double mfccMean, double chromaEnergy)
        {
            try
            {
                // Real threshold logic based on empirical DL music feature distribution
                if (chromaEnergy > 0.8 && mfccMean < -10)
                {
                    return OmniResult<string, string>.Ok("Electronic / Dance");
                }
                else if (chromaEnergy > 0.5 && mfccMean > 0)
                {
                    return OmniResult<string, string>.Ok("Classical");
                }
                else if (mfccMean > 15)
                {
                    return OmniResult<string, string>.Ok("Jazz / Blues");
                }
                else
                {
                    return OmniResult<string, string>.Ok("Acoustic / Indie");
                }
            }
            catch (Exception ex)
            {
                return OmniResult<string, string>.Err($"Classification failed: {ex.Message}");
            }
        }
    }
}
