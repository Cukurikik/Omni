using System;
using System.Collections.Generic;

namespace Omni.Business.MuseGANGenerator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HarmonyRules
    {
        // Define allowable scales (e.g., C Major / A minor white keys)
        private readonly HashSet<int> _allowedPitchClasses = new HashSet<int> { 0, 2, 4, 5, 7, 9, 11 };

        public OmniResult<List<int>> QuantizeToScale(List<int> rawMidiNotes)
        {
            if (rawMidiNotes == null || rawMidiNotes.Count == 0)
            {
                return new OmniResult<List<int>>(new ArgumentException("Note array cannot be empty"));
            }

            var quantizedNotes = new List<int>(rawMidiNotes.Count);

            // Business rule: Enforce diatonic scale adherence mathematically
            foreach (var note in rawMidiNotes)
            {
                if (note < 0 || note > 127)
                {
                    return new OmniResult<List<int>>(new ArgumentOutOfRangeException($"Invalid MIDI note: {note}"));
                }

                int pitchClass = note % 12;
                int octave = note / 12;

                if (_allowedPitchClasses.Contains(pitchClass))
                {
                    quantizedNotes.Add(note);
                }
                else
                {
                    // Snap to nearest allowed pitch class deterministically
                    int nearestPitch = SnapToNearest(pitchClass);
                    quantizedNotes.Add((octave * 12) + nearestPitch);
                }
            }

            return new OmniResult<List<int>>(quantizedNotes);
        }

        private int SnapToNearest(int pitchClass)
        {
            // Simple deterministic snap (e.g. C# (1) -> C (0) or D (2), prefer lower)
            int bestMatch = 0;
            int minDistance = 12;

            foreach (var allowed in _allowedPitchClasses)
            {
                int dist = Math.Abs(pitchClass - allowed);
                if (dist < minDistance)
                {
                    minDistance = dist;
                    bestMatch = allowed;
                }
            }

            return bestMatch;
        }
    }
}
