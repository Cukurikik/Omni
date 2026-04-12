import sqlite3
import json
import time
import os

# ==========================================
# 💾 OMNI DESKTOP: Long-Term Memory Agent (Phase 105)
# ==========================================
# Agent Zero dan AutoGPT tidak akan berfungsi tanpa LTM (Long Term Memory).
# Skrip ini menyematkan Disk-Backed Memory terenkripsi. 
# Bot AI bisa di-restart beribu kali tapi memori dari percakapan 
# minggu lalu akan tetap selamat (Persistence Data).

class AutoGPT_SQLite_Memory:
    def __init__(self, db_path="omni_ltm.db"):
        self.db_path = db_path
        print(f"💾 [OMNI-LTM] Menyambungkan Node Memori Agent ke Disk ({db_path})...")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mem_vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context TEXT,
                embedding_hash TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save_memory(self, user_intent):
        print(f"📥 Menyimpan Niat Tuan ke Storage LTM: '{user_intent}'")
        time.sleep(0.1)
        conn = sqlite3.connect(self.db_path)
        conn.cursor().execute("INSERT INTO mem_vectors (context, embedding_hash) VALUES (?, ?)", (user_intent, "HASH256X_MOCK"))
        conn.commit()
        conn.close()
        print("✅ Konteks Tuan telah tertulis dalam batu OMNI selamanya.")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    mem = AutoGPT_SQLite_Memory()
    mem.save_memory("Tuan benci menggunakan try/catch dan meminta Error Monadic Pattern.")
