// @omni-layer Business | @omni-source jakobhoeg/browser-ai | @omni-lang C#
// @omni-description Browser AI session manager: DDD aggregate for inference
// sessions, usage tracking, model deployment, and billing.

namespace Omni.Business.BrowserAI
{
    public enum SessionStatus { Active, Idle, Terminated, Error }

    public sealed class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;
        private OmniResult(T data, string err) { Data = data; Error = err; }
        public static OmniResult<T> Ok(T data) => new(data, null);
        public static OmniResult<T> Fail(string err) => new(default, err);
    }

    public class InferenceSession
    {
        public string Id { get; set; }
        public string UserId { get; set; }
        public string ModelId { get; set; }
        public SessionStatus Status { get; set; } = SessionStatus.Active;
        public int TotalTokens { get; set; }
        public int RequestCount { get; set; }
        public double TotalLatencyMs { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime LastActive { get; set; } = DateTime.UtcNow;
    }

    public class UsageQuota
    {
        public string UserId { get; set; }
        public int DailyTokenLimit { get; set; } = 100000;
        public int TokensUsedToday { get; set; }
        public int Remaining => DailyTokenLimit - TokensUsedToday;
    }

    public class BrowserAISessionManager
    {
        private readonly Dictionary<string, InferenceSession> _sessions = new();
        private readonly Dictionary<string, UsageQuota> _quotas = new();

        public OmniResult<InferenceSession> CreateSession(string id, string userId, string modelId)
        {
            var session = new InferenceSession { Id = id, UserId = userId, ModelId = modelId };
            _sessions[id] = session;
            if (!_quotas.ContainsKey(userId))
                _quotas[userId] = new UsageQuota { UserId = userId };
            return OmniResult<InferenceSession>.Ok(session);
        }

        public OmniResult<bool> RecordInference(string sessionId, int tokens, double latencyMs)
        {
            if (!_sessions.TryGetValue(sessionId, out var session))
                return OmniResult<bool>.Fail("Session not found");
            if (!_quotas.TryGetValue(session.UserId, out var quota))
                return OmniResult<bool>.Fail("No quota");
            if (quota.Remaining < tokens)
                return OmniResult<bool>.Fail("Token quota exceeded");
            session.TotalTokens += tokens;
            session.RequestCount++;
            session.TotalLatencyMs += latencyMs;
            session.LastActive = DateTime.UtcNow;
            quota.TokensUsedToday += tokens;
            return OmniResult<bool>.Ok(true);
        }

        public OmniResult<InferenceSession> GetSession(string id) =>
            _sessions.TryGetValue(id, out var s)
                ? OmniResult<InferenceSession>.Ok(s)
                : OmniResult<InferenceSession>.Fail("Not found");

        public Dictionary<string, object> Stats() => new()
        {
            ["total_sessions"] = _sessions.Count,
            ["active"] = _sessions.Values.Count(s => s.Status == SessionStatus.Active),
            ["total_tokens"] = _sessions.Values.Sum(s => s.TotalTokens),
            ["avg_latency_ms"] = _sessions.Values.Where(s => s.RequestCount > 0).Average(s => s.TotalLatencyMs / s.RequestCount)
        };
    }
}
