// OMNI Business Layer — C# Domain-Driven Model Registry
// DDD aggregate for managing AI model lifecycle and deployments.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Omni.Domain.ModelManagement
{
    public record ModelId(Guid Value)
    {
        public static ModelId New() => new(Guid.NewGuid());
        public static ModelId From(string id) => new(Guid.Parse(id));
    }

    public enum ModelStatus
    {
        Draft,
        Training,
        Validating,
        Ready,
        Deployed,
        Deprecated,
        Archived
    }

    public record ModelMetrics(
        double Accuracy,
        double F1Score,
        double Perplexity,
        double LatencyP50Ms,
        double LatencyP99Ms,
        long ParameterCount,
        double ModelSizeMb
    );

    public record DeploymentTarget(
        string Environment,
        string Region,
        int Replicas,
        string ComputeType,
        DateTime DeployedAt
    );

    /// <summary>
    /// DDD Aggregate Root for AI Model lifecycle management.
    /// </summary>
    public sealed class ModelAggregate
    {
        public ModelId Id { get; }
        public string Name { get; private set; }
        public string Version { get; private set; }
        public string Architecture { get; private set; }
        public ModelStatus Status { get; private set; }
        public ModelMetrics? Metrics { get; private set; }
        public IReadOnlyList<DeploymentTarget> Deployments => _deployments.AsReadOnly();
        public DateTime CreatedAt { get; }
        public DateTime UpdatedAt { get; private set; }

        private readonly List<DeploymentTarget> _deployments = new();
        private readonly List<IDomainEvent> _events = new();

        public IReadOnlyList<IDomainEvent> DomainEvents => _events.AsReadOnly();

        private ModelAggregate(ModelId id, string name, string version, string architecture)
        {
            Id = id;
            Name = name;
            Version = version;
            Architecture = architecture;
            Status = ModelStatus.Draft;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
        }

        public static ModelAggregate Create(string name, string version, string architecture)
        {
            if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Model name required");
            if (string.IsNullOrWhiteSpace(version)) throw new ArgumentException("Version required");

            var model = new ModelAggregate(ModelId.New(), name, version, architecture);
            model.AddEvent(new ModelCreatedEvent(model.Id, name, version));
            return model;
        }

        public void StartTraining()
        {
            EnsureStatus(ModelStatus.Draft, "Cannot start training");
            Status = ModelStatus.Training;
            UpdatedAt = DateTime.UtcNow;
            AddEvent(new ModelTrainingStartedEvent(Id));
        }

        public void CompleteTraining(ModelMetrics metrics)
        {
            EnsureStatus(ModelStatus.Training, "Not in training");
            Metrics = metrics ?? throw new ArgumentNullException(nameof(metrics));
            Status = ModelStatus.Validating;
            UpdatedAt = DateTime.UtcNow;
            AddEvent(new ModelTrainingCompletedEvent(Id, metrics));
        }

        public void ApproveForDeployment()
        {
            EnsureStatus(ModelStatus.Validating, "Cannot approve");
            if (Metrics is null) throw new InvalidOperationException("Metrics required");
            if (Metrics.Accuracy < 0.8) throw new InvalidOperationException("Accuracy below threshold");
            Status = ModelStatus.Ready;
            UpdatedAt = DateTime.UtcNow;
            AddEvent(new ModelApprovedEvent(Id));
        }

        public void Deploy(string environment, string region, int replicas, string computeType)
        {
            if (Status != ModelStatus.Ready && Status != ModelStatus.Deployed)
                throw new InvalidOperationException($"Cannot deploy model in {Status} status");

            var target = new DeploymentTarget(environment, region, replicas, computeType, DateTime.UtcNow);
            _deployments.Add(target);
            Status = ModelStatus.Deployed;
            UpdatedAt = DateTime.UtcNow;
            AddEvent(new ModelDeployedEvent(Id, environment, region));
        }

        public void Deprecate(string reason)
        {
            Status = ModelStatus.Deprecated;
            UpdatedAt = DateTime.UtcNow;
            AddEvent(new ModelDeprecatedEvent(Id, reason));
        }

        private void EnsureStatus(ModelStatus expected, string message)
        {
            if (Status != expected) throw new InvalidOperationException($"{message}: current={Status}");
        }

        private void AddEvent(IDomainEvent @event) => _events.Add(@event);
        public void ClearEvents() => _events.Clear();
    }

    // Domain Events
    public interface IDomainEvent { DateTime OccurredAt { get; } }
    public record ModelCreatedEvent(ModelId Id, string Name, string Version) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }
    public record ModelTrainingStartedEvent(ModelId Id) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }
    public record ModelTrainingCompletedEvent(ModelId Id, ModelMetrics Metrics) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }
    public record ModelApprovedEvent(ModelId Id) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }
    public record ModelDeployedEvent(ModelId Id, string Environment, string Region) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }
    public record ModelDeprecatedEvent(ModelId Id, string Reason) : IDomainEvent { public DateTime OccurredAt { get; } = DateTime.UtcNow; }

    // Repository interface
    public interface IModelRepository
    {
        Task<ModelAggregate?> GetByIdAsync(ModelId id);
        Task<IReadOnlyList<ModelAggregate>> ListByStatusAsync(ModelStatus status);
        Task SaveAsync(ModelAggregate model);
    }
}
