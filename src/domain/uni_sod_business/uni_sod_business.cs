using System;

namespace Omni.Domain.UniSOD
{
    public class UniSODBusinessException : Exception
    {
        public UniSODBusinessException(string message) : base(message) {}
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
    /// OMNI Engine: unisod-business
    /// Determines logic paths for unified salient depth objects mapped to inventory or spatial bounds.
    /// </summary>
    public class UniSODBusinessEngine
    {
        private readonly double _confidenceRequired;

        public UniSODBusinessEngine(double confidenceRequired = 0.9)
        {
            _confidenceRequired = confidenceRequired;
        }

        public Result<bool> ValidateSalientInventoryObject(double detectionConfidence, bool isDepthObject)
        {
            if (detectionConfidence < 0 || detectionConfidence > 1.0)
            {
                return new Result<bool>(new UniSODBusinessException("Inventory detection geometry broke 1.0 matrix barrier"));
            }

            if (!isDepthObject)
            {
                 return new Result<bool>(new UniSODBusinessException("2D flat space is forbidden in Salient Depth logic mapping"));
            }

            if (detectionConfidence < _confidenceRequired)
            {
                return new Result<bool>(new UniSODBusinessException($"Salient object confidence {detectionConfidence} is below {_confidenceRequired} strict constraint limit"));
            }

            return new Result<bool>(true);
        }
    }
}
