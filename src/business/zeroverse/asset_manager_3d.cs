// @omni-layer Business | @omni-source desaixie/zeroverse | @omni-lang C#
// @omni-description 3D asset manager: DDD aggregate for procedural mesh
// catalog, reconstruction jobs, and triplane asset versioning.

namespace Omni.Business.Recon3D
{
    public enum AssetStatus { Draft, Processing, Ready, Published, Archived }
    public enum MeshQuality { Low, Medium, High, Ultra }

    public sealed class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;
        private OmniResult(T data, string err) { Data = data; Error = err; }
        public static OmniResult<T> Ok(T data) => new(data, null);
        public static OmniResult<T> Fail(string err) => new(default, err);
    }

    public class Asset3D
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public int NVertices { get; set; }
        public int NViews { get; set; }
        public int Seed { get; set; }
        public MeshQuality Quality { get; set; }
        public AssetStatus Status { get; set; } = AssetStatus.Draft;
        public int Version { get; set; } = 1;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class ReconJob
    {
        public string Id { get; set; }
        public string AssetId { get; set; }
        public int NPrimitives { get; set; }
        public int NViews { get; set; }
        public string Status { get; set; } = "pending";
        public double? ProcessingTimeSec { get; set; }
    }

    public class AssetManager3D
    {
        private readonly Dictionary<string, Asset3D> _assets = new();
        private readonly List<ReconJob> _jobs = new();

        public OmniResult<Asset3D> CreateAsset(string id, string name, int seed, MeshQuality quality)
        {
            var asset = new Asset3D { Id = id, Name = name, Seed = seed, Quality = quality };
            _assets[id] = asset;
            return OmniResult<Asset3D>.Ok(asset);
        }

        public OmniResult<ReconJob> SubmitReconJob(string assetId, int nPrimitives, int nViews)
        {
            if (!_assets.ContainsKey(assetId))
                return OmniResult<ReconJob>.Fail($"Asset {assetId} not found");
            var job = new ReconJob
            {
                Id = Guid.NewGuid().ToString("N"),
                AssetId = assetId,
                NPrimitives = nPrimitives,
                NViews = nViews
            };
            _jobs.Add(job);
            _assets[assetId].Status = AssetStatus.Processing;
            return OmniResult<ReconJob>.Ok(job);
        }

        public OmniResult<Asset3D> CompleteJob(string jobId, int nVertices)
        {
            var job = _jobs.Find(j => j.Id == jobId);
            if (job == null) return OmniResult<Asset3D>.Fail("Job not found");
            job.Status = "completed";
            var asset = _assets[job.AssetId];
            asset.NVertices = nVertices;
            asset.NViews = job.NViews;
            asset.Status = AssetStatus.Ready;
            asset.Version++;
            return OmniResult<Asset3D>.Ok(asset);
        }

        public OmniResult<List<Asset3D>> ListAssets(AssetStatus? status = null)
        {
            var list = _assets.Values.AsEnumerable();
            if (status.HasValue) list = list.Where(a => a.Status == status.Value);
            return OmniResult<List<Asset3D>>.Ok(list.OrderByDescending(a => a.CreatedAt).ToList());
        }

        public Dictionary<string, int> Stats() => new()
        {
            ["total_assets"] = _assets.Count,
            ["ready"] = _assets.Values.Count(a => a.Status == AssetStatus.Ready),
            ["total_jobs"] = _jobs.Count,
            ["completed_jobs"] = _jobs.Count(j => j.Status == "completed")
        };
    }
}
