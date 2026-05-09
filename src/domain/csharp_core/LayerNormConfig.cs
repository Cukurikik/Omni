using System;

namespace Omni.Domain.Transformers
{
    public record LayerNormConfig
    {
        public int HiddenDimension { get; init; }
        public double Epsilon { get; init; }
        public bool ElementwiseAffine { get; init; }
        public string PrecisionPolicy { get; init; }

        public LayerNormConfig(int hiddenDim, double eps = 1e-5, bool affine = true, string precision = "fp16")
        {
            if (hiddenDim <= 0) throw new ArgumentOutOfRangeException(nameof(hiddenDim));
            if (eps <= 0) throw new ArgumentOutOfRangeException(nameof(eps));

            HiddenDimension = hiddenDim;
            Epsilon = eps;
            ElementwiseAffine = affine;
            PrecisionPolicy = precision;
        }

        public bool ValidateConfiguration()
        {
            return HiddenDimension > 0 && Epsilon > 0 && !string.IsNullOrWhiteSpace(PrecisionPolicy);
        }
    }
}
