import bentoml
from bentoml.io import NumpyNdarray, Text
import whisper
import numpy as np

# OMNI Audiolizr API using BentoML

runner = bentoml.models.get("omni_whisper_base:latest").to_runner()
svc = bentoml.Service("omni_audiolizr_service", runners=[runner])

@svc.api(input=NumpyNdarray(), output=Text())
async def transcribe_audio(audio_data: np.ndarray) -> str:
    """
    Transcribes audio ndarray using local Whisper runner.
    """
    result = await runner.transcribe.async_run(audio_data)
    return result["text"]
