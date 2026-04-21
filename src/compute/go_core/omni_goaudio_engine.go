// omni_goaudio_engine.go
// Production-Grade Pure Go Audio DSP Engine
// ==============================================================
// Absorbed from: DylanMeeus/GoAudio
//
// OMNI Layer: compute/go_core
// @since 2026.4.0

package go_core

import (
	"errors"
	"fmt"
	"math"
)

const GoaudioEngineVersion = "1.0.0-omni"

// OmniGoaudioEngine provides pure Go audio signal processing
// without CGo dependencies. Supports waveform generation,
// FIR filtering, normalization, and WAV header construction.
type OmniGoaudioEngine struct {
	SampleRate int
	BitDepth   int
	Channels   int
}

// NewOmniGoaudioEngine creates a new Go audio DSP engine.
func NewOmniGoaudioEngine(sampleRate, bitDepth, channels int) *OmniGoaudioEngine {
	if sampleRate <= 0 { sampleRate = 44100 }
	if bitDepth <= 0 { bitDepth = 16 }
	if channels <= 0 { channels = 1 }
	return &OmniGoaudioEngine{SampleRate: sampleRate, BitDepth: bitDepth, Channels: channels}
}

// GenerateSine produces a pure sine tone.
func (e *OmniGoaudioEngine) GenerateSine(frequency float64, durationSec float64, amplitude float64) (map[string]interface{}, error) {
	if frequency <= 0 || frequency > float64(e.SampleRate)/2 {
		return nil, errors.New(fmt.Sprintf("frequency must be (0, %d]", e.SampleRate/2))
	}
	if durationSec <= 0 { return nil, errors.New("duration must be > 0") }
	if amplitude < 0 || amplitude > 1 { return nil, errors.New("amplitude must be [0, 1]") }

	numSamples := int(float64(e.SampleRate) * durationSec)
	samples := make([]float64, numSamples)
	for i := 0; i < numSamples; i++ {
		t := float64(i) / float64(e.SampleRate)
		samples[i] = amplitude * math.Sin(2*math.Pi*frequency*t)
	}

	rms := e.computeRMS(samples)
	return map[string]interface{}{
		"status": "success", "data": map[string]interface{}{
			"samples": samples, "numSamples": numSamples, "frequency": frequency,
			"durationSec": durationSec, "rms": math.Round(rms*1000000) / 1000000,
		},
	}, nil
}

// GenerateSawtooth produces a sawtooth waveform.
func (e *OmniGoaudioEngine) GenerateSawtooth(frequency float64, durationSec float64, amplitude float64) (map[string]interface{}, error) {
	if frequency <= 0 { return nil, errors.New("frequency must be > 0") }
	numSamples := int(float64(e.SampleRate) * durationSec)
	samples := make([]float64, numSamples)
	for i := 0; i < numSamples; i++ {
		phase := math.Mod(frequency*float64(i)/float64(e.SampleRate), 1.0)
		samples[i] = amplitude * (2.0*phase - 1.0)
	}
	return map[string]interface{}{"status": "success", "data": map[string]interface{}{"samples": samples, "numSamples": numSamples}}, nil
}

// ApplyFIRFilter applies a Finite Impulse Response filter.
func (e *OmniGoaudioEngine) ApplyFIRFilter(samples []float64, coefficients []float64) (map[string]interface{}, error) {
	if len(samples) == 0 { return nil, errors.New("empty input samples") }
	if len(coefficients) == 0 { return nil, errors.New("empty filter coefficients") }

	output := make([]float64, len(samples))
	filterLen := len(coefficients)

	for i := 0; i < len(samples); i++ {
		var sum float64
		for j := 0; j < filterLen; j++ {
			idx := i - j
			if idx >= 0 {
				sum += samples[idx] * coefficients[j]
			}
		}
		output[i] = sum
	}

	return map[string]interface{}{
		"status": "success", "data": map[string]interface{}{
			"filtered": output, "numSamples": len(output), "filterOrder": filterLen,
		},
	}, nil
}

// Normalize scales samples to [-1.0, 1.0] range.
func (e *OmniGoaudioEngine) Normalize(samples []float64) (map[string]interface{}, error) {
	if len(samples) == 0 { return nil, errors.New("empty samples for normalization") }

	peak := 0.0
	for _, s := range samples {
		abs := math.Abs(s)
		if abs > peak { peak = abs }
	}
	if peak < 1e-10 {
		return map[string]interface{}{"status": "success", "data": map[string]interface{}{
			"samples": samples, "gainApplied": 0.0, "originalPeak": 0.0,
		}}, nil
	}

	gain := 1.0 / peak
	normalized := make([]float64, len(samples))
	for i, s := range samples {
		normalized[i] = s * gain
	}

	return map[string]interface{}{
		"status": "success", "data": map[string]interface{}{
			"samples": normalized, "gainApplied": math.Round(gain*10000) / 10000,
			"originalPeak": math.Round(peak*1000000) / 1000000,
			"gainDb": math.Round(20*math.Log10(gain)*100) / 100,
		},
	}, nil
}

// MixSignals mixes multiple audio signals with gains.
func (e *OmniGoaudioEngine) MixSignals(signals [][]float64, gains []float64) (map[string]interface{}, error) {
	if len(signals) == 0 { return nil, errors.New("no signals to mix") }
	if len(gains) != len(signals) { return nil, errors.New("gains count must match signals count") }

	maxLen := 0
	for _, sig := range signals {
		if len(sig) > maxLen { maxLen = len(sig) }
	}

	mixed := make([]float64, maxLen)
	for i, sig := range signals {
		for j := 0; j < len(sig); j++ {
			mixed[j] += sig[j] * gains[i]
		}
	}

	peak := 0.0
	for _, s := range mixed {
		abs := math.Abs(s)
		if abs > peak { peak = abs }
	}
	clipped := peak > 1.0
	if clipped {
		for i := range mixed { mixed[i] /= peak }
	}

	return map[string]interface{}{
		"status": "success", "data": map[string]interface{}{
			"mixed": mixed, "numSamples": maxLen, "numInputs": len(signals),
			"peakLevel": math.Round(peak*10000) / 10000, "clipped": clipped,
		},
	}, nil
}

// BuildWavHeader constructs a WAV file header.
func (e *OmniGoaudioEngine) BuildWavHeader(dataSize int) (map[string]interface{}, error) {
	bytesPerSample := e.BitDepth / 8
	blockAlign := e.Channels * bytesPerSample
	byteRate := e.SampleRate * blockAlign

	return map[string]interface{}{
		"status": "success", "data": map[string]interface{}{
			"chunkSize": 36 + dataSize, "format": "WAVE", "audioFormat": 1,
			"channels": e.Channels, "sampleRate": e.SampleRate, "byteRate": byteRate,
			"blockAlign": blockAlign, "bitsPerSample": e.BitDepth, "dataSize": dataSize,
			"totalFileSize": 44 + dataSize,
		},
	}, nil
}

func (e *OmniGoaudioEngine) computeRMS(samples []float64) float64 {
	if len(samples) == 0 { return 0 }
	var sum float64
	for _, s := range samples { sum += s * s }
	return math.Sqrt(sum / float64(len(samples)))
}
