// @omni-layer Business | @omni-source all-repos-combined | @omni-lang C#
// @omni-description OMNI Batch 17 orchestrator: DDD aggregate root for
// managing batch lifecycle, engine registration, and deployment coordination.

namespace Omni.Business.Batch17
{
    public enum BatchStatus { Initialized, Manifesting, Building, Testing, Deployed, Failed }
    public enum EngineLayer { Compute, System, Concurrency, Business, Interface }

    public sealed class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;
        private OmniResult(T data, string err) { Data = data; Error = err; }
        public static OmniResult<T> Ok(T data) => new(data, null);
        public static OmniResult<T> Fail(string err) => new(default, err);
    }

    public class EngineRecord
    {
        public string Name { get; set; }
        public EngineLayer Layer { get; set; }
        public string Language { get; set; }
        public string Repository { get; set; }
        public string FilePath { get; set; }
        public string Status { get; set; } = "registered";
    }

    public class BatchOrchestrator
    {
        private readonly Dictionary<string, EngineRecord> _engines = new();
        private BatchStatus _status = BatchStatus.Initialized;
        private int _batchId;
        private int _semester;

        public BatchOrchestrator(int batchId, int semester)
        {
            _batchId = batchId; _semester = semester;
        }

        public OmniResult<string> RegisterEngine(string name, EngineLayer layer, string language, string repository, string filePath)
        {
            _engines[name] = new EngineRecord
            {
                Name = name, Layer = layer, Language = language,
                Repository = repository, FilePath = filePath
            };
            return OmniResult<string>.Ok($"Registered {name} ({language}) in {layer}");
        }

        public OmniResult<Dictionary<string, int>> LayerSummary()
        {
            var summary = _engines.Values
                .GroupBy(e => e.Layer)
                .ToDictionary(g => g.Key.ToString(), g => g.Count());
            return OmniResult<Dictionary<string, int>>.Ok(summary);
        }

        public OmniResult<List<string>> LanguageReport()
        {
            var langs = _engines.Values.Select(e => e.Language).Distinct().OrderBy(l => l).ToList();
            return OmniResult<List<string>>.Ok(langs);
        }

        public OmniResult<string> SetStatus(BatchStatus status)
        {
            _status = status;
            return OmniResult<string>.Ok($"Batch {_batchId} status: {_status}");
        }

        public Dictionary<string, object> Stats() => new()
        {
            ["batch_id"] = _batchId,
            ["semester"] = _semester,
            ["status"] = _status.ToString(),
            ["total_engines"] = _engines.Count,
            ["layers"] = _engines.Values.Select(e => e.Layer).Distinct().Count(),
            ["languages"] = _engines.Values.Select(e => e.Language).Distinct().Count(),
            ["repositories"] = _engines.Values.Select(e => e.Repository).Distinct().Count()
        };
    }
}
