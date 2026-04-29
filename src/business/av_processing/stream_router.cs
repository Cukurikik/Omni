using System;
using System.Collections.Concurrent;
using System.Collections.Generic;

namespace Omni.Business.AVProcessing
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

    public class StreamMetadata
    {
        public string StreamId { get; set; }
        public string Codec { get; set; }
        public int Bitrate { get; set; }
        public List<string> Subscribers { get; set; } = new List<string>();
    }

    public class StreamRouter
    {
        private readonly ConcurrentDictionary<string, StreamMetadata> _activeStreams = new();

        public Result<string, string> RegisterStream(string streamId, string codec, int bitrate)
        {
            if (string.IsNullOrWhiteSpace(streamId)) return Result<string, string>.Err("Invalid Stream ID");
            
            var meta = new StreamMetadata { StreamId = streamId, Codec = codec, Bitrate = bitrate };
            if (_activeStreams.TryAdd(streamId, meta))
            {
                return Result<string, string>.Ok(streamId);
            }
            return Result<string, string>.Err("Stream ID already registered");
        }

        public Result<bool, string> Subscribe(string streamId, string clientId)
        {
            if (_activeStreams.TryGetValue(streamId, out var meta))
            {
                lock (meta.Subscribers)
                {
                    if (!meta.Subscribers.Contains(clientId))
                    {
                        meta.Subscribers.Add(clientId);
                    }
                }
                return Result<bool, string>.Ok(true);
            }
            return Result<bool, string>.Err("Stream not found");
        }

        public Result<List<string>, string> GetSubscribers(string streamId)
        {
             if (_activeStreams.TryGetValue(streamId, out var meta))
             {
                 lock(meta.Subscribers)
                 {
                     return Result<List<string>, string>.Ok(new List<string>(meta.Subscribers));
                 }
             }
             return Result<List<string>, string>.Err("Stream not found");
        }
    }
}
