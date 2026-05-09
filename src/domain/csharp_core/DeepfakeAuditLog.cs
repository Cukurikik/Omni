using System;

namespace Omni.Domain.Security
{
    public class DeepfakeAuditLog
    {
        public Guid LogId { get; }
        public string VideoHash { get; }
        public double FakeProbability { get; }
        public DateTime Timestamp { get; }

        public DeepfakeAuditLog(string videoHash, double fakeProbability)
        {
            if (string.IsNullOrEmpty(videoHash)) throw new ArgumentException("Video hash required");
            if (fakeProbability < 0 || fakeProbability > 1) throw new ArgumentOutOfRangeException("Probability must be between 0 and 1");

            LogId = Guid.NewGuid();
            VideoHash = videoHash;
            FakeProbability = fakeProbability;
            Timestamp = DateTime.UtcNow;
        }
    }
}
