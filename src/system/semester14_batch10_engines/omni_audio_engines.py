# Omni Audio Engines
class OmniAudioEngineBase:
    def health_check(self): return {"status": "healthy"}

class OmniWhisperEngine(OmniAudioEngineBase):
    def __init__(self): self.id = "omni-whisper-s14b10"
    def health_check(self): return {"status": "healthy", "engine_id": self.id}

class OmniBarkEngine(OmniAudioEngineBase):
    def __init__(self): self.id = "omni-bark-s14b10"
    def health_check(self): return {"status": "healthy", "engine_id": self.id}

class OmniMusicGenEngine(OmniAudioEngineBase):
    def __init__(self): self.id = "omni-musicgen-s14b10"
    def health_check(self): return {"status": "healthy", "engine_id": self.id}
