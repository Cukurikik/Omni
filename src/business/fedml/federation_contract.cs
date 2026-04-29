using System;
using System.Collections.Generic;

namespace Omni.Business.FedML
{
    /// <summary>
    /// OMNI FEDML: Domain-Driven Design (DDD) Federation Contract
    /// Enforces business rules and states for federated learning nodes joining a cluster.
    /// Source: FedML-AI/FedML
    /// </summary>
    
    public enum NodeStatus
    {
        Pending,
        Active,
        Suspended,
        Disconnected
    }

    public class FederationResult<T>
    {
        public T Value { get; }
        public string ErrorMessage { get; }
        public bool IsSuccess => string.IsNullOrEmpty(ErrorMessage);

        private FederationResult(T value, string error)
        {
            Value = value;
            ErrorMessage = error;
        }

        public static FederationResult<T> Ok(T value) => new FederationResult<T>(value, null);
        public static FederationResult<T> Fail(string error) => new FederationResult<T>(default, error);
    }

    public class FederationNode
    {
        public Guid NodeId { get; private set; }
        public string IpAddress { get; private set; }
        public int ComputeCapacity { get; private set; }
        public NodeStatus Status { get; private set; }
        public DateTime LastHeartbeat { get; private set; }

        private FederationNode(Guid id, string ip, int capacity)
        {
            NodeId = id;
            IpAddress = ip;
            ComputeCapacity = capacity;
            Status = NodeStatus.Pending;
            LastHeartbeat = DateTime.UtcNow;
        }

        public static FederationResult<FederationNode> Register(string ipAddress, int computeCapacity)
        {
            if (string.IsNullOrWhiteSpace(ipAddress))
                return FederationResult<FederationNode>.Fail("IP Address cannot be empty.");
                
            if (computeCapacity < 100)
                return FederationResult<FederationNode>.Fail("Compute capacity too low to join federation.");

            var node = new FederationNode(Guid.NewGuid(), ipAddress, computeCapacity);
            return FederationResult<FederationNode>.Ok(node);
        }

        public FederationResult<bool> Approve()
        {
            if (Status != NodeStatus.Pending)
                return FederationResult<bool>.Fail("Only pending nodes can be approved.");

            Status = NodeStatus.Active;
            return FederationResult<bool>.Ok(true);
        }

        public void RecordHeartbeat()
        {
            LastHeartbeat = DateTime.UtcNow;
            if (Status == NodeStatus.Disconnected)
            {
                Status = NodeStatus.Active;
            }
        }

        public FederationResult<bool> AuditStatus()
        {
            if (Status == NodeStatus.Active && (DateTime.UtcNow - LastHeartbeat).TotalMinutes > 5)
            {
                Status = NodeStatus.Disconnected;
                return FederationResult<bool>.Fail($"Node {NodeId} marked as disconnected due to heartbeat timeout.");
            }
            return FederationResult<bool>.Ok(true);
        }
    }
}
