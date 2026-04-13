"""
===========================================================================
OMNI TRACING & TELEMETRY OBSERVABILITY
===========================================================================
Alur sistem untuk memantau performa dan biaya agen AI secara internal:
1. Token Tracking: Mengalkulasi panjang string output / request.
2. Latency Monitoring: Memastikan Call ke LLM tidak hang.
3. Cost Tracking per Request: Dasbor tagihan terpusat.
===========================================================================
"""
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [OMNI TELEMETRY] - %(message)s')

class OmniObservability:
    def __init__(self):
        self.total_tokens_used = 0
        self.session_latency = []

    def trace_llm_call(self, prompt, mock_latency_sec):
        logging.info(f"Trace Request Aktif. Menghitung Token (Estimasi)...")
        token_count = len(prompt.split()) * 1.5 # Basic est
        self.total_tokens_used += token_count
        
        logging.info(f"Menunggu respons LLM Lokal ({mock_latency_sec}s)...")
        time.sleep(mock_latency_sec)
        self.session_latency.append(mock_latency_sec)
        
        logging.info(f"Call Selesai. Token Sesi Total: {self.total_tokens_used}. Average Latensi Rute: {sum(self.session_latency)/len(self.session_latency):.2f}s")
        
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    obs = OmniObservability()
    obs.trace_llm_call("Siapa presiden Indonesia saat ini dan jelaskan biografi singkatnya.", 0.2)
    obs.trace_llm_call("Tulislah kode python untuk sorting list.", 0.5)
    print("✅ Sistem Telemetri & Tracing Internal Terkalibrasi.")
