using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.MLExplain
{
    public class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T data) { Data = data; }
        public OmniResult(string error) { Error = error; }
    }

    public class ComplianceChecker
    {
        private readonly double _maxBiasThreshold;

        public ComplianceChecker(double maxBiasThreshold = 0.15)
        {
            _maxBiasThreshold = maxBiasThreshold;
        }

        public OmniResult<bool> EvaluateFeatureImportance(List<double> shapValues, List<string> featureNames, List<string> protectedFeatures)
        {
            if (shapValues == null || featureNames == null || shapValues.Count != featureNames.Count)
            {
                return new OmniResult<bool>("Dimension mismatch between SHAP values and feature names.");
            }

            // Sum absolute SHAP values to find total impact
            double totalImpact = shapValues.Sum(Math.Abs);
            if (totalImpact == 0) return new OmniResult<bool>(true);

            for (int i = 0; i < featureNames.Count; i++)
            {
                if (protectedFeatures.Contains(featureNames[i]))
                {
                    double relativeImpact = Math.Abs(shapValues[i]) / totalImpact;
                    
                    if (relativeImpact > _maxBiasThreshold)
                    {
                        return new OmniResult<bool>($"Compliance violation: Protected feature '{featureNames[i]}' exceeds impact threshold ({relativeImpact:F3} > {_maxBiasThreshold:F3})");
                    }
                }
            }

            return new OmniResult<bool>(true);
        }
    }
}
