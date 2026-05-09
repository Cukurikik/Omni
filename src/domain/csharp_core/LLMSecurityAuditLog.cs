using System;

namespace Omni.Domain.Security
{
    public class LLMSecurityAuditLog
    {
        public Guid EventId { get; private set; }
        public DateTime Timestamp { get; private set; }
        public string SourceIp { get; private set; }
        public string Action { get; private set; }
        public bool WasBlocked { get; private set; }
        public double ThreatScore { get; private set; }

        public LLMSecurityAuditLog(string sourceIp, string action, bool wasBlocked, double threatScore)
        {
            EventId = Guid.NewGuid();
            Timestamp = DateTime.UtcNow;
            SourceIp = sourceIp;
            Action = action;
            WasBlocked = wasBlocked;
            ThreatScore = threatScore;
        }

        public string ToSyslogFormat()
        {
            return $"[{Timestamp:O}] OMNI-LLM-FW: src={SourceIp} action={Action} blocked={WasBlocked} score={ThreatScore}";
        }
    }
}
