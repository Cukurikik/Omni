using System;

namespace Omni.Semester14.Batch8.BigScience
{
    public class OmniResult<T, E>
    {
        public T Payload { get; }
        public E Error { get; }
        public bool IsOk { get; }

        private OmniResult(T payload, E error, bool isOk)
        {
            Payload = payload;
            Error = error;
            IsOk = isOk;
        }

        public static OmniResult<T, E> Ok(T payload) => new OmniResult<T, E>(payload, default, true);
        public static OmniResult<T, E> Err(E error) => new OmniResult<T, E>(default, error, false);
    }

    public class DataAuditLogger
    {
        private readonly int _maxLogSizeBytes;
        
        public DataAuditLogger(int maxLogSizeBytes = 1048576) // 1MB max per log entry
        {
            _maxLogSizeBytes = maxLogSizeBytes;
        }

        public OmniResult<bool, string> RecordDeduplicationEvent(string chunkId, bool wasRemoved, string hashSignature)
        {
            if (string.IsNullOrWhiteSpace(chunkId) || string.IsNullOrWhiteSpace(hashSignature))
            {
                return OmniResult<bool, string>.Err("OMNI_AUDIT_ERR: Missing required audit fields.");
            }

            string logEntry = $"[{DateTime.UtcNow:O}] CHUNK:{chunkId} REMOVED:{wasRemoved} HASH:{hashSignature}";
            
            if (System.Text.Encoding.UTF8.GetByteCount(logEntry) > _maxLogSizeBytes)
            {
                 return OmniResult<bool, string>.Err("OMNI_LIMIT: Audit log entry exceeds size limit.");
            }

            // In production, this emits to an internal Kafka stream via OMNI bridge
            // Console.WriteLine(logEntry); 
            
            return OmniResult<bool, string>.Ok(true);
        }
    }
}
