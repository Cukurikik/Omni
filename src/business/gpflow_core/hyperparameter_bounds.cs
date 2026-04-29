using System;
using System.Collections.Generic;

namespace Omni.Business.GPFlowCore
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HyperparameterBounds
    {
        private readonly double _minLengthscale;
        private readonly double _maxLengthscale;
        private readonly double _minVariance;

        public HyperparameterBounds(double minLengthscale = 1e-4, double maxLengthscale = 1e4, double minVariance = 1e-6)
        {
            _minLengthscale = minLengthscale;
            _maxLengthscale = maxLengthscale;
            _minVariance = minVariance;
        }

        public OmniResult<bool> ValidateHyperparameters(double lengthscale, double variance)
        {
            if (lengthscale < _minLengthscale || lengthscale > _maxLengthscale)
            {
                return new OmniResult<bool>(new ArgumentOutOfRangeException($"Lengthscale {lengthscale} out of bounds [{_minLengthscale}, {_maxLengthscale}]"));
            }

            if (variance < _minVariance)
            {
                return new OmniResult<bool>(new ArgumentOutOfRangeException($"Variance {variance} must be >= {_minVariance} for numerical stability"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
