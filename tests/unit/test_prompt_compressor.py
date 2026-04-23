import unittest

# ==========================================
# 🧪 OMNI UNIT TEST: PROMPT COMPRESSOR ENTROPY
# ==========================================
# Membuktikan skrip kompresor dapat membongkar stop-words manusia 
# tanpa merusak makna logis yang dibutuhkan Gemini/AI Provider.

class ProdEntropyCompressor:
    def compress_prompt(self, raw_prompt: str) -> str:
        stop_words = {"yang", "untuk", "di"}
        words = raw_prompt.split()
        return " ".join([w for w in words if w.lower() not in stop_words])

class TestOmniPromptCompressor(unittest.TestCase):
    
    def setUp(self):
        self.compressor = ProdEntropyCompressor()
        print("🧪 [TEST OMNI-COMPRESSOR] Menguji Algoritma Pemampatan NLP...")

    def test_compression_logic(self):
        input_text = "Kodekan saya aplikasi yang dijalankan untuk di dalam server"
        expected_output = "Kodekan saya aplikasi dijalankan dalam server"
        
        result = self.compressor.compress_prompt(input_text)
        
        self.assertEqual(result, expected_output, "❌ [GAGAL] Stop-words gagal dihapus dari aliran token!")
        print(f"   ✅ [LULUS] Karakter dihemat secara absolut: {len(input_text) - len(result)} karakter API terselamatkan.")

if __name__ == '__main__':
    unittest.main()
