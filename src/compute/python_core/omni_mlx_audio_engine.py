"""OmniMlxAudioEngine.

Wrapper for Blaizzy/mlx-audio.
Apple MLX based text-to-speech and speech-to-text.
"""
from typing import Dict, Any
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniMlxAudioEngine:
    """OMNI Engine for MLX Audio processing."""

    def __init__(self, tts_model: str = "mlx-tts-base"):
        """Initialize the MLX audio engine."""
        self.tts_model = tts_model

    def diagnostics(self) -> Dict[str, Any]:
        """Returns diagnostic metadata."""
        return {
            "engine": "OmniMlxAudioEngine",
            "status": "ready",
            "backend": "apple_silicon",
            "tts_model": self.tts_model
        }

    def transcribe_audio(self, audio_path: str) -> Result[str, Exception]:
        """Runs speech-to-text on an audio file using MLX.
        
        Args:
            audio_path: Path to wav/mp3 file.
            
        Returns:
            Result wrapping transcribed text.
        """
        try:
            import mlx.core as mx
            from mlx_audio.transcribe import transcribe
            
            # Using mlx array to ensure we capture the mlx specific engine capability
            result = transcribe(audio_path)
            return Ok(result["text"])
        except ImportError:
            return Err(Exception("mlx-audio package is not installed."))
        except Exception as e:
            return Err(e)
