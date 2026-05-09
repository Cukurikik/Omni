# moe_lixaudio_tts_router.py — Compute
# Layer: Compute — Smart Audio Pipeline Router (TTS/STT/STS)
# Inspired by: lixaudio (Smart pipeline to perform TTS/TTT/STS/STT)

from enum import Enum

class AudioTask(Enum):
    TTS = "Text-to-Speech"
    STT = "Speech-to-Text"
    STS = "Speech-to-Speech"
    TTT = "Text-to-Text"

class LixAudioRouter:
    """
    Routes multimodal audio/text requests to the appropriate OMNI MoE audio expert.
    """
    def __init__(self):
        self.active_pipelines = {
            AudioTask.TTS: "expert_vits_vocoder_01",
            AudioTask.STT: "expert_whisper_v3_large",
            AudioTask.STS: "expert_voice_conversion_hubert",
            AudioTask.TTT: "expert_llm_translator"
        }

    def route_request(self, input_type: str, output_type: str, payload: bytes) -> dict:
        task = self._determine_task(input_type, output_type)
        expert_id = self.active_pipelines.get(task)
        
        if not expert_id:
            raise ValueError(f"No expert found for task: {task}")
            
        return {
            "target_expert": expert_id,
            "task_type": task.value,
            "payload_size": len(payload),
            "status": "routed"
        }

    def _determine_task(self, in_type: str, out_type: str) -> AudioTask:
        if in_type == "text" and out_type == "audio":
            return AudioTask.TTS
        elif in_type == "audio" and out_type == "text":
            return AudioTask.STT
        elif in_type == "audio" and out_type == "audio":
            return AudioTask.STS
        elif in_type == "text" and out_type == "text":
            return AudioTask.TTT
        else:
            raise ValueError("Invalid multimodal pipeline requested.")
