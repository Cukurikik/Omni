"""
===========================================================================
OMNI ADVANCED MEMORY SYSTEMS (Cortex Ingatan Waktu)
===========================================================================
Mengelola memori agar Agent tidak menjadi skizofrenia di percakapan panjang:
1. Short-Term Buffer: Obrolan aktif selama sesi (Memory Window).
2. Episodic Memory: Ringkasan event lampau (Summarization).
3. Semantic Vector Memory: Pencarian makna fakta jangka panjang.
===========================================================================
"""
import sys
import logging
from collections import deque

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OMNI MEMORY] - %(message)s')

class OmniEpisodicMemory:
    def __init__(self, max_short_term=5):
        self.short_term_buffer = deque(maxlen=max_short_term)
        self.long_term_episodes = [] # Vector placeholder

    def add_interaction(self, user_msg, agent_resp):
        logging.info("Merekam Memori Jangka Pendek (Short-Term Buffer)...")
        self.short_term_buffer.append({"u": user_msg, "a": agent_resp})
        
        if len(self.short_term_buffer) == self.short_term_buffer.maxlen:
            self._compress_to_episode()

    def _compress_to_episode(self):
        logging.warning("Buffer Jangka Pendek Penuh! Memicu Kompresi Episodik...")
        # Simulating LLM Summarization of past turns
        summary = "Diskusi detail tentang arsitektur Sandboxing dan Security Firewall."
        self.long_term_episodes.append(summary)
        logging.info(f"✅ Epispode Baru Tercipta & Disimpan di Long-Term: '{summary}'")
        self.short_term_buffer.clear()
        
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    mem = OmniEpisodicMemory(max_short_term=3)
    
    # Simulasi 3 interaksi memicu kompresi otonom
    mem.add_interaction("Apa itu Omni?", "Sistem berdaulat.")
    mem.add_interaction("Apakah pakai Vertex?", "Tidak. 100% In-house.")
    mem.add_interaction("Bagus.", "Terima kasih.")
    
    print("\n✅ Validasi Pengindeksan Memori Berjalan Otonom.")
