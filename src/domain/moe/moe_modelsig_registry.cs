// moe_modelsig_registry.cs — Domain Layer: Model Signature Registry
// C# entity storing structural fingerprints of LLM models for compatibility comparisons.

using System;
using System.Collections.Generic;

namespace Omni.Domain.MoE.ModelSig
{
    public class ModelRegistry
    {
        private readonly Dictionary<string, string> _fingerprintMap = new Dictionary<string, string>();

        public void RegisterModel(string modelId, string sha256Fingerprint)
        {
            if (string.IsNullOrEmpty(modelId) || string.IsNullOrEmpty(sha256Fingerprint))
                throw new ArgumentException("Invalid model identification data.");

            _fingerprintMap[modelId] = sha256Fingerprint;
        }

        public bool AreStructurallyIdentical(string modelIdA, string modelIdB)
        {
            if (!_fingerprintMap.TryGetValue(modelIdA, out var sigA) || 
                !_fingerprintMap.TryGetValue(modelIdB, out var sigB))
            {
                throw new KeyNotFoundException("One or both models are not registered.");
            }

            return string.Equals(sigA, sigB, StringComparison.OrdinalIgnoreCase);
        }
    }
}
