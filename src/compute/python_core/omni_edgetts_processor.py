# Omni EdgeTTS Processor Engine
from typing import List, Dict

def estimate_tts_processing_latency(text_length_chars: int, model_params_m: float, edge_flops_g: float) -> float:
    """Estimate on-device TTS generation latency in milliseconds."""
    if edge_flops_g <= 0:
        return -1.0
    # Abstract heuristic: chars * params / edge_flops
    operations = text_length_chars * model_params_m * 0.5
    latency_s = operations / (edge_flops_g * 1000)
    return round(latency_s * 1000.0, 2)

def mel_spectrogram_dummy_extract(audio_waveform: List[float], n_mels: int = 80) -> List[List[float]]:
    """Generate a deterministic dummy mel-spectrogram for testing edge pipelines."""
    frames = len(audio_waveform) // 256
    spectrogram = []
    for i in range(frames):
        # Deterministic dummy data based on waveform
        frame_energy = abs(audio_waveform[i*256]) if i*256 < len(audio_waveform) else 0.0
        mel_frame = [round(frame_energy * (j / n_mels), 4) for j in range(n_mels)]
        spectrogram.append(mel_frame)
    return spectrogram
