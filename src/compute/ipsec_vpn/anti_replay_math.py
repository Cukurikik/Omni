import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class IPsecMath:
    def __init__(self):
        # Simulated 64-bit anti-replay window state (bitmap)
        self.replay_window = 0
        self.window_size = 64
        self.highest_seq = 0

    def check_esp_anti_replay(self, seq_num: int) -> OmniResult:
        if seq_num <= 0:
            return OmniResult(error="Sequence number must be strictly positive")

        # Deterministic IPsec ESP Anti-Replay window math
        try:
            if seq_num > self.highest_seq:
                # Packet is new and advances the window
                diff = seq_num - self.highest_seq
                if diff >= self.window_size:
                    self.replay_window = 1
                else:
                    self.replay_window = (self.replay_window << diff) | 1
                self.highest_seq = seq_num
                return OmniResult(value={"accept": True, "reason": "ADVANCED_WINDOW"})
                
            # Packet is within or behind the window
            diff = self.highest_seq - seq_num
            if diff >= self.window_size:
                return OmniResult(value={"accept": False, "reason": "REPLAY_TOO_OLD"})
                
            # Check bitmap
            mask = 1 << diff
            if (self.replay_window & mask) != 0:
                return OmniResult(value={"accept": False, "reason": "REPLAY_DUPLICATE"})
                
            # Accept and update bitmap
            self.replay_window |= mask
            return OmniResult(value={"accept": True, "reason": "IN_WINDOW"})
            
        except Exception as e:
            return OmniResult(error=str(e))
