using System;
using System.Collections.Generic;

namespace Omni.Business.Milvus
{
    /// <summary>
    /// OMNI MILVUS: Collection and Partition Manager
    /// C# domain logic representing the organization of vector data namespaces.
    /// Source: milvus-io/milvus
    /// </summary>
    
    public class ManagerError : Exception
    {
        public ManagerError(string message) : base(message) {}
    }

    public class Partition
    {
        public string Name { get; }
        public long VectorCount { get; private set; }

        public Partition(string name)
        {
            Name = name;
            VectorCount = 0;
        }

        public void AddVectors(long count)
        {
            VectorCount += count;
        }
    }

    public class Collection
    {
        public string Name { get; }
        public int Dimension { get; }
        public string MetricType { get; } // L2, IP, COSINE
        private readonly Dictionary<string, Partition> _partitions;

        public Collection(string name, int dimension, string metricType = "L2")
        {
            Name = name;
            Dimension = dimension;
            MetricType = metricType;
            _partitions = new Dictionary<string, Partition>();
            
            // Create default partition
            _partitions["_default"] = new Partition("_default");
        }

        public void CreatePartition(string name)
        {
            if (_partitions.ContainsKey(name))
            {
                throw new ManagerError($"Partition {name} already exists.");
            }
            _partitions[name] = new Partition(name);
        }

        public Partition GetPartition(string name)
        {
            if (!_partitions.ContainsKey(name))
            {
                throw new ManagerError($"Partition {name} not found.");
            }
            return _partitions[name];
        }

        public long GetTotalVectorCount()
        {
            long total = 0;
            foreach (var part in _partitions.Values)
            {
                total += part.VectorCount;
            }
            return total;
        }
    }
}
