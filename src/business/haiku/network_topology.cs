using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Haiku
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }
        private Result(bool isSuccess, T value, E error) { IsSuccess = isSuccess; Value = value; Error = error; }
        public static Result<T, E> Success(T value) => new Result<T, E>(true, value, default!);
        public static Result<T, E> Failure(E error) => new Result<T, E>(false, default!, error);
    }

    public enum LayerType { Dense, Conv2D, MaxPool, Flatten }

    public class LayerConfig
    {
        public LayerType Type { get; set; }
        public int Units { get; set; }
        public string Activation { get; set; } = "relu";
    }

    public class NetworkTopology
    {
        private readonly List<LayerConfig> _layers = new List<LayerConfig>();

        public Result<bool, string> AddLayer(LayerConfig layer)
        {
            if (layer == null) return Result<bool, string>.Failure("Layer cannot be null");
            if (layer.Units <= 0) return Result<bool, string>.Failure("Units must be greater than zero");
            
            _layers.Add(layer);
            return Result<bool, string>.Success(true);
        }

        public Result<int, string> CalculateTotalParameters(int inputFeatures)
        {
            if (_layers.Count == 0) return Result<int, string>.Failure("No layers in topology");
            if (inputFeatures <= 0) return Result<int, string>.Failure("Input features must be positive");

            int totalParams = 0;
            int currentFeatures = inputFeatures;

            foreach (var layer in _layers)
            {
                if (layer.Type == LayerType.Dense)
                {
                    // weights + biases
                    totalParams += (currentFeatures * layer.Units) + layer.Units;
                    currentFeatures = layer.Units;
                }
                else
                {
                    return Result<int, string>.Failure($"Parameter calculation for {layer.Type} not yet supported in zero-mock structural implementation.");
                }
            }

            return Result<int, string>.Success(totalParams);
        }
    }
}
