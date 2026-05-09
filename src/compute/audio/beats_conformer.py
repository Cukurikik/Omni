#=============================================================================
# OMNI COMPUTE LAYER — BEATS CONFORMER AUDIO CAPTIONER (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Improving Audio Captioning with Fine-grained features.
# INSPIRED BY: slSeanWU/beats-conformer-bart-audio-captioner
#=============================================================================

import numpy as np
import omni_bridge.system.tensor as ffi
import omni_bridge.domain.error as err

class AudioCaptioner:
    """
    BEATs + Conformer + BART Audio Captioner.
    """
    def __init__(self, model_prefix: str):
        self.model_prefix = model_prefix
        
    def load_model(self) -> err.Result:
        try:
            # Initialize BEATs acoustic model
            self.beats_handle = ffi.mmap_safetensors(f"{self.model_prefix}_beats.safetensors")
            # Initialize Conformer encoder
            self.conformer_handle = ffi.mmap_safetensors(f"{self.model_prefix}_conformer.safetensors")
            # Initialize BART decoder
            self.bart_handle = ffi.mmap_safetensors(f"{self.model_prefix}_bart.safetensors")
            return err.Ok()
        except Exception as e:
            return err.Err(f"Failed to load AudioCaptioner: {str(e)}")

    def caption_audio_stream(self, audio_data: np.ndarray) -> err.Result[str]:
        """
        Takes raw 16kHz audio data and generates a text caption.
        """
        try:
            # 1. Extract BEATs features
            beats_feats = ffi.execute_beats_extraction(self.beats_handle, audio_data)
            
            # 2. Refine via Conformer
            conformer_out = ffi.execute_conformer(self.conformer_handle, beats_feats)
            
            # 3. Decode caption via BART
            caption_str = ffi.execute_bart_decode(self.bart_handle, conformer_out)
            
            return err.Ok(caption_str)
        except Exception as e:
            return err.Err(f"Audio captioning failed: {str(e)}")
