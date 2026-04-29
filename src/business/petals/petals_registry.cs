using System;
using System.Collections.Generic;

namespace Omni.Semester14.Batch8.Petals
{
    /// <summary>
    /// OMNI Monadic Result
    /// </summary>
    public class OmniResult<T, E>
    {
        public T Payload { get; }
        public E Error { get; }
        public bool IsOk { get; }

        private OmniResult(T payload, E error, bool isOk)
        {
            Payload = payload;
            Error = error;
            IsOk = isOk;
        }

        public static OmniResult<T, E> Ok(T payload) => new OmniResult<T, E>(payload, default, true);
        public static OmniResult<T, E> Err(E error) => new OmniResult<T, E>(default, error, false);
    }

    public class PetalsNodeRegistry
    {
        private const int MAX_NETWORK_NODES = 10000;
        private readonly Dictionary<string, int> _activeNodes = new Dictionary<string, int>();

        public OmniResult<bool, string> RegisterNode(string nodeId, int shardCapacity)
        {
            if (string.IsNullOrWhiteSpace(nodeId))
            {
                return OmniResult<bool, string>.Err("OMNI_REG_001: Node ID cannot be empty.");
            }

            if (shardCapacity <= 0)
            {
                return OmniResult<bool, string>.Err("OMNI_REG_002: Shard capacity must be greater than 0.");
            }

            if (_activeNodes.Count >= MAX_NETWORK_NODES)
            {
                return OmniResult<bool, string>.Err($"OMNI_REG_003: Network reached maximum capacity of {MAX_NETWORK_NODES} nodes.");
            }

            _activeNodes[nodeId] = shardCapacity;
            return OmniResult<bool, string>.Ok(true);
        }

        public OmniResult<int, string> GetTotalNetworkCapacity()
        {
            int total = 0;
            foreach (var capacity in _activeNodes.Values)
            {
                total += capacity;
            }
            return OmniResult<int, string>.Ok(total);
        }
    }
}
