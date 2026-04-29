// OMNI FRAMEWORK: BATCH 38
// ENGINE: MACHINE LEARNING CONTEXT (C#)
// DOMAIN: BUSINESS / ENTERPRISE ML
// ZERO MOCK - PRODUCTION READY
// ==========================================

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.MachineLearning
{
    public class MLContextError : Exception
    {
        public string Code { get; }
        public MLContextError(string code, string message) : base(message)
        {
            Code = code;
        }
    }

    public class MLResult<T>
    {
        public T Value { get; }
        public MLContextError Error { get; }

        public MLResult(T value) { Value = value; Error = null; }
        public MLResult(MLContextError error) { Value = default; Error = error; }
    }

    public class DataView
    {
        public List<double[]> Rows { get; } = new List<double[]>();

        public void AddRow(double[] row)
        {
            Rows.Add(row);
        }
    }

    public class OmniMLContext
    {
        private readonly object _lock = new object();
        private Dictionary<string, DataView> _datasets = new Dictionary<string, DataView>();

        public MLResult<bool> LoadData(string name, DataView data)
        {
            lock (_lock)
            {
                if (_datasets.ContainsKey(name))
                {
                    return new MLResult<bool>(new MLContextError("DATA_EXISTS", "Dataset already loaded."));
                }
                _datasets[name] = data;
                return new MLResult<bool>(true);
            }
        }

        public MLResult<double> CalculateMean(string name, int columnIndex)
        {
            lock (_lock)
            {
                if (!_datasets.TryGetValue(name, out var data))
                {
                    return new MLResult<double>(new MLContextError("NOT_FOUND", "Dataset not found."));
                }

                if (data.Rows.Count == 0)
                    return new MLResult<double>(0);

                double sum = 0;
                foreach (var row in data.Rows)
                {
                    if (columnIndex >= row.Length)
                        return new MLResult<double>(new MLContextError("OUT_OF_BOUNDS", "Column index out of bounds."));
                    sum += row[columnIndex];
                }

                return new MLResult<double>(sum / data.Rows.Count);
            }
        }
    }
}
