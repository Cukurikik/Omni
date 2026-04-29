using System;
using System.Collections.Generic;

namespace Omni.Business.AudioMIDI
{
    public class OmniResult<T>
    {
        public T Data { get; }
        public string Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T data) { Data = data; }
        public OmniResult(string error) { Error = error; }
    }

    public class MIDINote
    {
        public double StartTime { get; set; }
        public double Duration { get; set; }
        public int Pitch { get; set; }
        public int Velocity { get; set; }
    }

    public class TranscriptionManager
    {
        public OmniResult<List<MIDINote>> BuildMidiTrack(List<double> onsetTimes, List<int> detectedPitches)
        {
            if (onsetTimes == null || detectedPitches == null)
            {
                return new OmniResult<List<MIDINote>>("Inputs cannot be null.");
            }
            if (onsetTimes.Count != detectedPitches.Count)
            {
                return new OmniResult<List<MIDINote>>("Mismatch between onsets and pitch dimensions.");
            }

            var notes = new List<MIDINote>();
            for (int i = 0; i < onsetTimes.Count; i++)
            {
                // Validate MIDI pitch bounds
                if (detectedPitches[i] < 0 || detectedPitches[i] > 127)
                {
                    return new OmniResult<List<MIDINote>>($"Invalid MIDI pitch: {detectedPitches[i]}");
                }

                // Deterministic duration mathematical estimation
                double duration = 0.25; 
                if (i < onsetTimes.Count - 1)
                {
                    duration = Math.Min(onsetTimes[i+1] - onsetTimes[i], 2.0); // Max 2 seconds
                }

                notes.Add(new MIDINote
                {
                    StartTime = onsetTimes[i],
                    Duration = duration,
                    Pitch = detectedPitches[i],
                    Velocity = 100 // Standard velocity
                });
            }

            return new OmniResult<List<MIDINote>>(notes);
        }
    }
}
