// ===========================================================================
// OMNI LASP ENGINE (TRUE KNOWLEDGE EXTRACTION)
// ===========================================================================
// Absorbed Paradigm : keijiro/Lasp
// Logic Inherited   : Unity Audio-Reactive RMS (Root Mean Square) Level Algorithms
// Domain Layer      : Domain / C# Core
// ===========================================================================

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Omni.Domain.Audio
{
    /// <summary>
    /// By studying LASP, Mother learned that 'audio reactive visuals' rely on math, 
    /// primarily calculating the Root Mean Square (RMS) of a chunk of floating point 
    /// audio buffers and normalizing that volume float to visually animate an object.
    /// 
    /// This C# engine isolates that explicit math array loop showing structural
    /// mastery over low-latency signal extraction formulas typically trapped in Unity.
    /// </summary>
    public class OmniLaspEngine
    {
        private float _dynamicPeak = 0.001f;
        public int CyclesComputed { get; private set; }

        public OmniLaspEngine()
        {
            CyclesComputed = 0;
        }

        public double CalculateRmsLevel(float[] buffer)
        {
            if (buffer == null || buffer.Length == 0) return 0;

            double sumSquares = 0;
            for (int i = 0; i < buffer.Length; i++)
            {
                sumSquares += buffer[i] * buffer[i];
            }

            CyclesComputed++;
            return Math.Sqrt(sumSquares / buffer.Length);
        }

        public float GetNormalizedAudioLevel(float[] buffer)
        {
            float rms = (float)CalculateRmsLevel(buffer);
            
            // Dynamic normalization (simulating Keijiro's peak tracking decay)
            if (rms > _dynamicPeak) _dynamicPeak = rms;
            else _dynamicPeak *= 0.99f; // Decay factor

            return Math.Clamp(rms / _dynamicPeak, 0.0f, 1.0f);
        }

        public object Diagnostics()
        {
            return new {
                engine = "OmniLaspEngine",
                layer = "C# / .NET Unity Domain logic",
                rms_frames_processed = CyclesComputed,
                learned_logic = new string[] { "audio-reactive-root-mean-square", "dynamic-peak-normalization", "low-latency-float-iteration" }
            };
        }
    }

    // ---------------------------------------------------------------------------
    // Execution Entry (Self-Contained Logic Verification Boundary)
    // ---------------------------------------------------------------------------
    class Program
    {
        static void Main()
        {
            var engine = new OmniLaspEngine();
            
            // Simulating an audio buffer hitting a loud kick drum transient
            float[] simulatedBuffer = new float[] { 0.1f, 0.5f, -0.9f, 0.8f, -0.2f, 0.0f };
            
            double rawRms = engine.CalculateRmsLevel(simulatedBuffer);
            float normalized = engine.GetNormalizedAudioLevel(simulatedBuffer);

            var report = new {
                status = "success",
                operation = "native-lasp-rms-calculation",
                raw_rms_amplitude = rawRms,
                animation_driver_factor = normalized 
            };

            Console.WriteLine(JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }));
            Console.WriteLine(JsonSerializer.Serialize(engine.Diagnostics(), new JsonSerializerOptions { WriteIndented = true }));
        }
    }
}
