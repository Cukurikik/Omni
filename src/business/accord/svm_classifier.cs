using System;
using System.Collections.Generic;
using System.Linq;

// OMNI C# Business Layer: Accord.NET Support Vector Machine
// Pure mathematical implementation of linear SVM for domain classification.

namespace Omni.Business.Accord
{
    public struct SvmResult<T>
    {
        public T Value;
        public string Error;
        public bool IsOk;

        public static SvmResult<T> Ok(T val) => new SvmResult<T> { Value = val, IsOk = true };
        public static SvmResult<T> Err(string err) => new SvmResult<T> { Error = err, IsOk = false };
    }

    public class LinearSVM
    {
        private double[] _weights;
        private double _bias;
        private readonly double _learningRate;
        private readonly double _lambda; // Regularization parameter

        public LinearSVM(double learningRate = 0.001, double lambda = 0.01)
        {
            _learningRate = learningRate;
            _lambda = lambda;
        }

        public SvmResult<bool> Train(double[][] inputs, int[] labels, int epochs = 1000)
        {
            if (inputs == null || labels == null || inputs.Length != labels.Length || inputs.Length == 0)
                return SvmResult<bool>.Err("Invalid training data dimensions.");

            int features = inputs[0].Length;
            _weights = new double[features];
            _bias = 0.0;

            // Ensure labels are -1 and 1
            int[] mappedLabels = labels.Select(l => l <= 0 ? -1 : 1).ToArray();

            for (int epoch = 0; epoch < epochs; epoch++)
            {
                for (int i = 0; i < inputs.Length; i++)
                {
                    // Hinge Loss condition: y_i * (w*x_i - b) >= 1
                    double condition = mappedLabels[i] * (DotProduct(inputs[i], _weights) - _bias);

                    if (condition >= 1)
                    {
                        // Correct classification, apply regularization gradient
                        for (int w = 0; w < _weights.Length; w++)
                        {
                            _weights[w] -= _learningRate * (2 * _lambda * _weights[w]);
                        }
                    }
                    else
                    {
                        // Incorrect classification, apply loss gradient + regularization
                        for (int w = 0; w < _weights.Length; w++)
                        {
                            _weights[w] -= _learningRate * (2 * _lambda * _weights[w] - inputs[i][w] * mappedLabels[i]);
                        }
                        _bias -= _learningRate * mappedLabels[i];
                    }
                }
            }

            return SvmResult<bool>.Ok(true);
        }

        public SvmResult<int> Predict(double[] input)
        {
            if (_weights == null || input.Length != _weights.Length)
                return SvmResult<int>.Err("Model is not trained or input dimension mismatch.");

            double projection = DotProduct(input, _weights) - _bias;
            return SvmResult<int>.Ok(projection >= 0 ? 1 : -1);
        }

        private double DotProduct(double[] a, double[] b)
        {
            double result = 0;
            for (int i = 0; i < a.Length; i++) result += a[i] * b[i];
            return result;
        }
    }
}
