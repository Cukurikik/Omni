// @omni-layer Business | @omni-source sidharthrajaram/StyleTTS2 | @omni-lang C#
// @omni-description Voice model registry: DDD aggregate for speaker profiles,
// style vectors, synthesis quotas, and voice cloning management.

namespace Omni.Business.TTS
{
    public enum VoiceStatus { Active, Training, Suspended, Archived }

    public sealed class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;
        private OmniResult(T data, string err) { Data = data; Error = err; }
        public static OmniResult<T> Ok(T data) => new(data, null);
        public static OmniResult<T> Fail(string err) => new(default, err);
    }

    public class SpeakerProfile
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Language { get; set; }
        public VoiceStatus Status { get; set; } = VoiceStatus.Active;
        public int SynthesisCount { get; set; }
        public double TotalDurationSec { get; set; }
        public double[] StyleVector { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class SynthesisQuota
    {
        public string UserId { get; set; }
        public int MonthlyLimit { get; set; } = 10000;
        public int Used { get; set; }
        public int Remaining => MonthlyLimit - Used;
    }

    public class VoiceModelRegistry
    {
        private readonly Dictionary<string, SpeakerProfile> _speakers = new();
        private readonly Dictionary<string, SynthesisQuota> _quotas = new();

        public OmniResult<SpeakerProfile> RegisterSpeaker(string id, string name, string lang, double[] styleVec)
        {
            var profile = new SpeakerProfile
            {
                Id = id, Name = name, Language = lang,
                StyleVector = styleVec ?? Array.Empty<double>()
            };
            _speakers[id] = profile;
            return OmniResult<SpeakerProfile>.Ok(profile);
        }

        public OmniResult<SpeakerProfile> GetSpeaker(string id)
        {
            return _speakers.TryGetValue(id, out var sp)
                ? OmniResult<SpeakerProfile>.Ok(sp)
                : OmniResult<SpeakerProfile>.Fail($"Speaker {id} not found");
        }

        public OmniResult<bool> RecordSynthesis(string speakerId, string userId, double durationSec)
        {
            if (!_speakers.TryGetValue(speakerId, out var sp))
                return OmniResult<bool>.Fail("Speaker not found");
            if (!_quotas.ContainsKey(userId))
                _quotas[userId] = new SynthesisQuota { UserId = userId };
            var quota = _quotas[userId];
            if (quota.Remaining <= 0)
                return OmniResult<bool>.Fail("Quota exhausted");
            sp.SynthesisCount++;
            sp.TotalDurationSec += durationSec;
            quota.Used++;
            return OmniResult<bool>.Ok(true);
        }

        public OmniResult<List<SpeakerProfile>> ListSpeakers(string language = null)
        {
            var list = _speakers.Values.AsEnumerable();
            if (language != null) list = list.Where(s => s.Language == language);
            return OmniResult<List<SpeakerProfile>>.Ok(list.OrderBy(s => s.Name).ToList());
        }

        public Dictionary<string, object> Stats() => new()
        {
            ["total_speakers"] = _speakers.Count,
            ["active"] = _speakers.Values.Count(s => s.Status == VoiceStatus.Active),
            ["total_syntheses"] = _speakers.Values.Sum(s => s.SynthesisCount),
            ["total_duration_hours"] = _speakers.Values.Sum(s => s.TotalDurationSec) / 3600.0
        };
    }
}
