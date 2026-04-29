using System;
using System.Collections.Generic;
using System.Linq;

namespace Omni.Business.AudioGen
{
    public class TrackResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        private TrackResult(T data, string error)
        {
            Data = data;
            Error = error;
        }

        public static TrackResult<T> Ok(T data) => new TrackResult<T>(data, null);
        public static TrackResult<T> Fail(string error) => new TrackResult<T>(default, error);
    }

    public class AudioClip
    {
        public string Id { get; set; } = Guid.NewGuid().ToString();
        public double StartTimeSeconds { get; set; }
        public double DurationSeconds { get; set; }
        public int TrackIndex { get; set; }
        public string FilePath { get; set; }
    }

    public class TrackComposer
    {
        private readonly List<AudioClip> _clips = new List<AudioClip>();

        public TrackResult<bool> AddClip(AudioClip clip)
        {
            if (clip == null) return TrackResult<bool>.Fail("Clip cannot be null");
            if (clip.DurationSeconds <= 0) return TrackResult<bool>.Fail("Duration must be positive");
            if (clip.StartTimeSeconds < 0) return TrackResult<bool>.Fail("Start time cannot be negative");

            // Check for collision on the same track
            bool collision = _clips.Any(c => 
                c.TrackIndex == clip.TrackIndex &&
                !(clip.StartTimeSeconds >= c.StartTimeSeconds + c.DurationSeconds || 
                  clip.StartTimeSeconds + clip.DurationSeconds <= c.StartTimeSeconds)
            );

            if (collision)
            {
                return TrackResult<bool>.Fail($"Collision detected on track {clip.TrackIndex}");
            }

            _clips.Add(clip);
            return TrackResult<bool>.Ok(true);
        }

        public TrackResult<double> GetTotalDuration()
        {
            if (_clips.Count == 0) return TrackResult<double>.Ok(0.0);
            
            double duration = _clips.Max(c => c.StartTimeSeconds + c.DurationSeconds);
            return TrackResult<double>.Ok(duration);
        }

        public TrackResult<List<AudioClip>> GetClipsInRange(double startSec, double endSec)
        {
            if (startSec >= endSec) return TrackResult<List<AudioClip>>.Fail("Invalid range");

            var inRange = _clips.Where(c => 
                (c.StartTimeSeconds < endSec) && 
                (c.StartTimeSeconds + c.DurationSeconds > startSec)
            ).OrderBy(c => c.StartTimeSeconds).ToList();

            return TrackResult<List<AudioClip>>.Ok(inRange);
        }
    }
}
