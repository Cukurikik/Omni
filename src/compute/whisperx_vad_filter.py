class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

def apply_vad(audio):
    if audio is None: return Result(error="No audio")
    return Result(value="FilteredAudio")
