using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.Cybersec
{
    public class Result<T, E>
    {
        public bool IsSuccess { get; }
        public T Value { get; }
        public E Error { get; }

        private Result(bool isSuccess, T value, E error)
        {
            IsSuccess = isSuccess;
            Value = value;
            Error = error;
        }

        public static Result<T, E> Ok(T value) => new Result<T, E>(true, value, default);
        public static Result<T, E> Err(E error) => new Result<T, E>(false, default, error);
    }

    public class IoCRecord // Indicator of Compromise
    {
        public string Indicator { get; set; } // IP, Hash, Domain
        public string Type { get; set; } // "IP", "SHA256", "Domain"
        public int ConfidenceScore { get; set; } // 0-100
        public string Campaign { get; set; }
    }

    public class ThreatIntelFeed
    {
        private readonly Dictionary<string, IoCRecord> _iocDatabase = new();

        public Result<bool, string> IngestFeed(List<IoCRecord> records)
        {
            if (records == null || records.Count == 0)
                return Result<bool, string>.Err("Empty feed provided");

            lock (_iocDatabase)
            {
                foreach (var record in records)
                {
                    if (!string.IsNullOrWhiteSpace(record.Indicator))
                    {
                        // Upsert logic
                        if (_iocDatabase.TryGetValue(record.Indicator, out var existing))
                        {
                            // Keep higher confidence
                            if (record.ConfidenceScore > existing.ConfidenceScore)
                            {
                                _iocDatabase[record.Indicator] = record;
                            }
                        }
                        else
                        {
                            _iocDatabase[record.Indicator] = record;
                        }
                    }
                }
            }
            return Result<bool, string>.Ok(true);
        }

        public Result<IoCRecord, string> CheckIndicator(string indicator)
        {
            if (string.IsNullOrWhiteSpace(indicator))
                return Result<IoCRecord, string>.Err("Invalid indicator");

            lock (_iocDatabase)
            {
                if (_iocDatabase.TryGetValue(indicator, out var record))
                {
                    return Result<IoCRecord, string>.Ok(record);
                }
            }
            
            return Result<IoCRecord, string>.Err("Indicator not found");
        }
    }
}
