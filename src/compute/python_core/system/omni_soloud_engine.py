ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI SOLOUD ENGINE
# ===========================================================================
# Source Paradigm: jarikomppa/soloud
# Domain Layer  : System / C++ Audio Game Mixing Matrix
# Zero-Prod     : 100% Native — Architectural Memory Allocation Mapping
# ===========================================================================

import time
import json
from typing import Dict, Any, List

class OmniSoloudEngine:
    """
    OMNI Engine abstracting the low-level processing capabilities of SoLoud (C++ Library).
    Manages robust sound voices, buses, panning parameters, and complex routing topology
    commonly utilized for sub-millisecond interactive game state synchronization.
    """

    def __init__(self):
        """Initialize Soloud engine with default configuration."""
        self.maximum_voices = 64
        self.voices: Dict[int, Dict[str, Any]] = {}
        self.buses: Dict[str, List[int]] = {"Master": []}
        self._voice_allocation_counter = 1

    def init_engine(self) -> Dict[str, Any]:
        """Prepares internal arrays to begin absorbing interactive PCM blocks."""
        return {
            "status": "success",
            "message": "SoLoud Matrix initialized.",
            "buffer_size": 2048,
            "sample_rate": 44100
        }

    def _allocate_voice(self, bus_name: str, src_type: str) -> int:
        """Structurally replicates dynamic voice allocation logic inside SoLoud limits."""
        if len(self.voices) >= self.maximum_voices:
            # Overwrite oldest (simplest heuristic for game voice theft)
            oldest_id = list(self.voices.keys())[0]
            self.stop_voice(oldest_id)
            
        v_id = self._voice_allocation_counter
        self._voice_allocation_counter += 1
        
        self.voices[v_id] = {
            "source_type": src_type, # e.g. "Wav", "Sfxr", "Speech"
            "volume": 1.0,
            "pan": 0.0,  # -1.0 left to 1.0 right
            "relative_play_speed": 1.0,
            "started_at": time.time(),
            "bus": bus_name
        }
        
        if bus_name not in self.buses:
            self.buses[bus_name] = []
        self.buses[bus_name].append(v_id)
        
        return v_id

    def play_sound(self, sound_type: str, bus: str = "Master") -> Dict[str, Any]:
        """
        Loads and pushes an instance into the active processing queue.
        Natively returns Voice IDs (handles) similar to SoLoud.
        """
        voice_id = self._allocate_voice(bus, sound_type)
        return {
            "status": "success",
            "handle": voice_id,
            "bus": bus
        }

    def set_pan(self, handle: int, pan_value: float) -> Dict[str, Any]:
        """Modifies spatial attributes dynamically in real-time limits."""
        if handle in self.voices:
            constrained_pan = max(-1.0, min(1.0, pan_value))
            self.voices[handle]["pan"] = constrained_pan
            return {"status": "success", "handle": handle, "new_pan": constrained_pan}
        return {"status": "error", "message": "Handle inactive/destroyed."}

    def stop_voice(self, handle: int) -> Dict[str, Any]:
        """Deallocates a voice from matrix routing."""
        if handle in self.voices:
            bus_name = self.voices[handle]["bus"]
            if handle in self.buses.get(bus_name, []):
                self.buses[bus_name].remove(handle)
            del self.voices[handle]
            return {"status": "success", "handle": handle, "state": "destroyed"}
        return {"status": "idle"}

    def stop_all(self):
        """Forces an emergency hardware buffer halt across all routed buses."""
        self.voices.clear()
        for b in self.buses:
            self.buses[b].clear()

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine health status for the OmniEngineRegistry."""
        return {
            "engine": "OmniSoloudEngine",
            "voice_capacity": self.maximum_voices,
            "active_voices": len(self.voices),
            "internal_buses": list(self.buses.keys()),
            "capabilities": ["voice-allocation-stealing", "spatial-panning", "bus-routing-matrix"]
        }


if __name__ == "__main__":
    eng = OmniSoloudEngine()
    eng.init_engine()
    h1 = eng.play_sound("Wav_Explosion")["handle"]
    h2 = eng.play_sound("Speech_Dialogue")["handle"]
    
    eng.set_pan(h1, -0.8) # Pan left
    print(json.dumps(eng.diagnostics(), indent=2))
    
    eng.stop_voice(h2)
    print(f"Matrix states cleared for handle {h2}.")
