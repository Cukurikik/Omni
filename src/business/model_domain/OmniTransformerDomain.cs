// @omni-layer Business | @omni-lang C# | @omni-batch 18 | @omni-semester 16
// @omni-description C# DDD aggregate for transformer model lifecycle management,
// inference request handling, and knowledge edit domain logic.

using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Transformer.Domain
{
    public enum ModelStatus { Active, Inactive, Training, Deprecated }
    public enum InferenceStatus { Queued, Processing, Completed, Failed }

    public record ModelId(string Value);
    public record EditId(string Value);

    public class TransformerModel
    {
        public ModelId Id { get; }
        public string Type { get; }
        public string Version { get; private set; }
        public int DModel { get; }
        public int NHeads { get; }
        public long ParamsCount { get; }
        public ModelStatus Status { get; private set; }
        public DateTime CreatedAt { get; }
        public DateTime UpdatedAt { get; private set; }
        private readonly List<KnowledgeEdit> _edits = new();
        public IReadOnlyList<KnowledgeEdit> Edits => _edits.AsReadOnly();

        public TransformerModel(ModelId id, string type, string version, int dModel, int nHeads, long paramsCount)
        {
            Id = id ?? throw new ArgumentNullException(nameof(id));
            Type = type;
            Version = version;
            DModel = dModel;
            NHeads = nHeads;
            ParamsCount = paramsCount;
            Status = ModelStatus.Active;
            CreatedAt = DateTime.UtcNow;
            UpdatedAt = DateTime.UtcNow;
        }

        public void Activate() { Status = ModelStatus.Active; UpdatedAt = DateTime.UtcNow; }
        public void Deactivate() { Status = ModelStatus.Inactive; UpdatedAt = DateTime.UtcNow; }
        public void Deprecate() { Status = ModelStatus.Deprecated; UpdatedAt = DateTime.UtcNow; }

        public KnowledgeEdit ApplyEdit(string subject, string relation, string oldObj, string newObj, string editorId)
        {
            if (Status != ModelStatus.Active)
                throw new InvalidOperationException($"Cannot edit model in {Status} status");
            var edit = new KnowledgeEdit(
                new EditId($"edit-{Guid.NewGuid():N}"),
                Id, editorId, subject, relation, oldObj, newObj
            );
            _edits.Add(edit);
            UpdatedAt = DateTime.UtcNow;
            return edit;
        }

        public void UpdateVersion(string newVersion)
        {
            Version = newVersion;
            UpdatedAt = DateTime.UtcNow;
        }
    }

    public class KnowledgeEdit
    {
        public EditId Id { get; }
        public ModelId ModelId { get; }
        public string EditorId { get; }
        public string Subject { get; }
        public string Relation { get; }
        public string OldObject { get; }
        public string NewObject { get; }
        public bool Verified { get; private set; }
        public double VerificationScore { get; private set; }
        public DateTime CreatedAt { get; }

        public KnowledgeEdit(EditId id, ModelId modelId, string editorId,
            string subject, string relation, string oldObj, string newObj)
        {
            Id = id; ModelId = modelId; EditorId = editorId;
            Subject = subject; Relation = relation;
            OldObject = oldObj; NewObject = newObj;
            Verified = false; VerificationScore = 0.0;
            CreatedAt = DateTime.UtcNow;
        }

        public void Verify(double score)
        {
            VerificationScore = Math.Clamp(score, 0.0, 1.0);
            Verified = score >= 0.8;
        }
    }

    public class InferenceRequest
    {
        public string RequestId { get; }
        public ModelId ModelId { get; }
        public string UserId { get; }
        public int[] InputTokens { get; }
        public int MaxOutputTokens { get; }
        public InferenceStatus Status { get; private set; }
        public DateTime CreatedAt { get; }

        public InferenceRequest(ModelId modelId, string userId, int[] inputTokens, int maxOutput = 128)
        {
            RequestId = $"req-{Guid.NewGuid():N}";
            ModelId = modelId; UserId = userId;
            InputTokens = inputTokens; MaxOutputTokens = maxOutput;
            Status = InferenceStatus.Queued;
            CreatedAt = DateTime.UtcNow;
        }

        public void MarkProcessing() => Status = InferenceStatus.Processing;
        public void MarkCompleted() => Status = InferenceStatus.Completed;
        public void MarkFailed() => Status = InferenceStatus.Failed;
    }

    public class ModelRegistry
    {
        private readonly Dictionary<string, TransformerModel> _models = new();

        public void Register(TransformerModel model) => _models[model.Id.Value] = model;
        public TransformerModel? Get(string modelId) => _models.GetValueOrDefault(modelId);
        public IEnumerable<TransformerModel> GetActive() => _models.Values.Where(m => m.Status == ModelStatus.Active);
        public int Count => _models.Count;
    }
}
