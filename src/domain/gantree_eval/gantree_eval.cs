using System;

namespace Omni.Domain.GANTree
{
    public class GANTreeDomainException : Exception
    {
        public GANTreeDomainException(string message) : base(message) {}
    }

    public class Result<T>
    {
        public T Value { get; }
        public Exception Error { get; }

        public Result(T value)
        {
            Value = value;
            Error = null;
        }

        public Result(Exception error)
        {
            Value = default;
            Error = error;
        }

        public bool IsOk() => Error == null;

        public T Unwrap()
        {
            if (!IsOk()) throw Error;
            return Value;
        }
    }

    /// <summary>
    /// OMNI Engine: gantree-eval
    /// Evaluator rules for hierarchical GAN logic in business scenarios.
    /// </summary>
    public class GANTreeEvalEngine
    {
        private readonly double _qualityThreshold;

        public GANTreeEvalEngine(double qualityThreshold = 0.85)
        {
            _qualityThreshold = qualityThreshold;
        }

        public Result<bool> ValidateGanAssetQuality(double generatorScore, double discriminatorLoss)
        {
            if (generatorScore < 0 || generatorScore > 1.0)
            {
                return new Result<bool>(new GANTreeDomainException("GAN Generator limits broke 0.0-1.0 geometry boundaries"));
            }

            if (discriminatorLoss < 0)
            {
                return new Result<bool>(new GANTreeDomainException("Discriminator loss matrix topologically inverted"));
            }

            // High generator score vs low discriminator loss = quality asset
            double assetQualityIndex = generatorScore * Math.Exp(-discriminatorLoss);

            if (assetQualityIndex < _qualityThreshold)
            {
                return new Result<bool>(new GANTreeDomainException($"Asset rejected: Index {assetQualityIndex} below bounds"));
            }

            return new Result<bool>(true);
        }
    }
}
