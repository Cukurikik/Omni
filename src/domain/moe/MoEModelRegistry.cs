// MoEModelRegistry.cs — MoE Model Registry Domain Service
// Layer: Domain / Business — MoE Model Lifecycle Management
//
// DDD aggregate root for MoE model lifecycle: registration, version
// management, expert configuration, deployment tracking, and audit log.

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Domain.MoE
{
    public enum ModelStatus
    {
        Draft,
        Registered,
        Deploying,
        Active,
        Deprecated,
        Archived
    }

    public enum ExpertStatus
    {
        Active,
        Inactive,
        Pruned,
        Quantized,
        Error
    }

    public sealed record ModelId(string Value)
    {
        public override string ToString() => Value;
    }

    public sealed record ExpertId(int Value)
    {
        public override string ToString() => $"expert-{Value}";
    }

    public sealed class ExpertSpec
    {
        public ExpertId Id { get; }
        public int HiddenDim { get; }
        public int FeedForwardDim { get; }
        public ExpertStatus Status { get; private set; }
        public int DeviceId { get; set; }
        public long ParameterCount { get; }
        public double MemoryMB { get; }

        public ExpertSpec(int id, int hiddenDim, int ffDim, long paramCount)
        {
            Id = new ExpertId(id);
            HiddenDim = hiddenDim;
            FeedForwardDim = ffDim;
            Status = ExpertStatus.Active;
            DeviceId = 0;
            ParameterCount = paramCount;
            MemoryMB = paramCount * 4.0 / (1024.0 * 1024.0); // FP32
        }

        public void Prune() => Status = ExpertStatus.Pruned;
        public void Activate() => Status = ExpertStatus.Active;
        public void Deactivate() => Status = ExpertStatus.Inactive;
        public void MarkQuantized() => Status = ExpertStatus.Quantized;
    }

    public sealed class RouterSpec
    {
        public string Strategy { get; set; } = "top_k";
        public int TopK { get; set; } = 2;
        public double CapacityFactor { get; set; } = 1.25;
        public double LoadBalanceWeight { get; set; } = 0.01;
        public double NoiseStd { get; set; } = 0.1;
    }

    public sealed class AuditEntry
    {
        public DateTime Timestamp { get; }
        public string Action { get; }
        public string Details { get; }
        public string Actor { get; }

        public AuditEntry(string action, string details, string actor = "system")
        {
            Timestamp = DateTime.UtcNow;
            Action = action;
            Details = details;
            Actor = actor;
        }
    }

    /// <summary>
    /// Aggregate root for MoE model lifecycle.
    /// </summary>
    public sealed class MoEModelAggregate
    {
        public ModelId Id { get; }
        public string Name { get; }
        public string Version { get; private set; }
        public ModelStatus Status { get; private set; }
        public int HiddenDim { get; }
        public int NumLayers { get; }
        public int NumHeads { get; }
        public RouterSpec Router { get; }

        private readonly List<ExpertSpec> _experts = new();
        private readonly List<AuditEntry> _audit = new();

        public IReadOnlyList<ExpertSpec> Experts => _experts.AsReadOnly();
        public IReadOnlyList<AuditEntry> AuditLog => _audit.AsReadOnly();

        public int ActiveExpertCount => _experts.Count(e => e.Status == ExpertStatus.Active);
        public long TotalParameters => _experts.Sum(e => e.ParameterCount);
        public double TotalMemoryMB => _experts.Sum(e => e.MemoryMB);

        public MoEModelAggregate(string id, string name, int hiddenDim,
            int numLayers, int numHeads, int numExperts, int ffDim)
        {
            Id = new ModelId(id);
            Name = name;
            Version = "1.0.0";
            Status = ModelStatus.Draft;
            HiddenDim = hiddenDim;
            NumLayers = numLayers;
            NumHeads = numHeads;
            Router = new RouterSpec { TopK = 2 };

            long paramsPerExpert = (long)hiddenDim * ffDim * 2 + hiddenDim + ffDim;
            for (int i = 0; i < numExperts; i++)
            {
                _experts.Add(new ExpertSpec(i, hiddenDim, ffDim, paramsPerExpert));
            }

            _audit.Add(new AuditEntry("CREATED",
                $"Model {name} created with {numExperts} experts, dim={hiddenDim}"));
        }

        public void Register()
        {
            if (Status != ModelStatus.Draft)
                throw new InvalidOperationException(
                    $"Cannot register model in {Status} status");
            if (!_experts.Any(e => e.Status == ExpertStatus.Active))
                throw new InvalidOperationException("Model has no active experts");

            Status = ModelStatus.Registered;
            _audit.Add(new AuditEntry("REGISTERED",
                $"Model registered with {ActiveExpertCount} active experts"));
        }

        public void Deploy()
        {
            if (Status != ModelStatus.Registered)
                throw new InvalidOperationException(
                    $"Cannot deploy model in {Status} status");

            Status = ModelStatus.Deploying;
            _audit.Add(new AuditEntry("DEPLOYING", "Deployment initiated"));
        }

        public void Activate()
        {
            if (Status != ModelStatus.Deploying)
                throw new InvalidOperationException(
                    $"Cannot activate model in {Status} status");

            Status = ModelStatus.Active;
            _audit.Add(new AuditEntry("ACTIVATED",
                $"Model is now serving with {ActiveExpertCount} experts"));
        }

        public void Deprecate()
        {
            Status = ModelStatus.Deprecated;
            _audit.Add(new AuditEntry("DEPRECATED", "Model marked as deprecated"));
        }

        public List<int> PruneExperts(double pruneRatio, int minExperts)
        {
            var activeExperts = _experts.Where(e => e.Status == ExpertStatus.Active).ToList();
            int numToPrune = Math.Max(0,
                (int)(activeExperts.Count * pruneRatio) - Math.Max(0, activeExperts.Count - minExperts));
            numToPrune = Math.Min(numToPrune, activeExperts.Count - minExperts);

            // Prune from the end (in production, use usage/sensitivity scores)
            var pruned = new List<int>();
            for (int i = activeExperts.Count - 1; i >= 0 && pruned.Count < numToPrune; i--)
            {
                activeExperts[i].Prune();
                pruned.Add(activeExperts[i].Id.Value);
            }

            _audit.Add(new AuditEntry("PRUNED",
                $"Pruned {pruned.Count} experts: [{string.Join(", ", pruned)}]"));

            return pruned;
        }

        public void BumpVersion(string newVersion)
        {
            var oldVersion = Version;
            Version = newVersion;
            _audit.Add(new AuditEntry("VERSION_BUMP",
                $"Version changed from {oldVersion} to {newVersion}"));
        }

        public void AssignExpertsToDevices(int numDevices)
        {
            var activeExperts = _experts.Where(e => e.Status == ExpertStatus.Active).ToList();
            int perDevice = (int)Math.Ceiling((double)activeExperts.Count / numDevices);
            for (int i = 0; i < activeExperts.Count; i++)
            {
                activeExperts[i].DeviceId = Math.Min(i / perDevice, numDevices - 1);
            }
            _audit.Add(new AuditEntry("DEVICE_ASSIGNMENT",
                $"Assigned {activeExperts.Count} experts across {numDevices} devices"));
        }
    }

    /// <summary>
    /// Repository interface for MoE model persistence.
    /// </summary>
    public interface IMoEModelRepository
    {
        MoEModelAggregate? FindById(ModelId id);
        List<MoEModelAggregate> FindByStatus(ModelStatus status);
        void Save(MoEModelAggregate model);
        void Delete(ModelId id);
    }

    /// <summary>
    /// Domain service for MoE model operations.
    /// </summary>
    public sealed class MoEModelService
    {
        private readonly IMoEModelRepository _repository;

        public MoEModelService(IMoEModelRepository repository)
        {
            _repository = repository;
        }

        public MoEModelAggregate CreateModel(string name, int hiddenDim,
            int numLayers, int numHeads, int numExperts, int ffDim)
        {
            var id = $"moe-{Guid.NewGuid():N}";
            var model = new MoEModelAggregate(id, name, hiddenDim,
                numLayers, numHeads, numExperts, ffDim);
            _repository.Save(model);
            return model;
        }

        public void RegisterAndDeploy(ModelId id)
        {
            var model = _repository.FindById(id)
                ?? throw new KeyNotFoundException($"Model {id} not found");
            model.Register();
            model.Deploy();
            _repository.Save(model);
        }

        public List<int> PruneModel(ModelId id, double pruneRatio)
        {
            var model = _repository.FindById(id)
                ?? throw new KeyNotFoundException($"Model {id} not found");
            var pruned = model.PruneExperts(pruneRatio, minExperts: 2);
            model.BumpVersion($"{model.Version}-pruned");
            _repository.Save(model);
            return pruned;
        }
    }
}
