import time
import json

# ==========================================
# 📊 PILAR #8: MODEL EVALUATION & DRIFT DETECTOR
# ==========================================
# Setelah QLoRA melatih model, SIAPA yang memantau kualitasnya?
# File ini mengukur akurasi model secara berkala dan mendeteksi "drift"
# (kemerosotan kualitas) sebelum ia menyebar ke produksi.

class OmniModelEvaluator:
    """Memantau kualitas seluruh model di registri. Mendeteksi drift."""
    
    def __init__(self):
        self.eval_history = []
        self.drift_threshold = 0.15  # 15% penurunan = alarm
        print("📊 [MODEL-EVALUATOR] Penjaga Mutu Model OMNI Aktif.")

    def evaluate_model(self, model_id: str, test_cases: list) -> dict:
        """Menjalankan serangkaian test case terhadap model dan menghitung skor."""
        print(f"\n   🔬 [EVALUATING] Model: {model_id} | {len(test_cases)} test cases...")
        
        correct = 0
        for tc in test_cases:
            # Simulasi: model menjawab benar jika prompt pendek (simplifikasi)
            predicted = len(tc["input"]) < 50
            expected = tc["expected_pass"]
            if predicted == expected:
                correct += 1
        
        accuracy = correct / len(test_cases) if test_cases else 0
        
        result = {
            "model_id": model_id,
            "accuracy": round(accuracy, 4),
            "total_cases": len(test_cases),
            "passed": correct,
            "timestamp": time.time(),
        }
        
        self.eval_history.append(result)
        print(f"   📊 Akurasi: {accuracy*100:.1f}% ({correct}/{len(test_cases)})")
        return result

    def detect_drift(self, model_id: str) -> bool:
        """Membandingkan evaluasi terakhir vs sebelumnya. Alarm jika menurun."""
        history = [h for h in self.eval_history if h["model_id"] == model_id]
        
        if len(history) < 2:
            print(f"   ℹ️ Belum cukup data historis untuk deteksi drift pada {model_id}.")
            return False
        
        prev = history[-2]["accuracy"]
        curr = history[-1]["accuracy"]
        delta = prev - curr
        
        if delta > self.drift_threshold:
            print(f"   🚨 [DRIFT DETECTED] {model_id}: {prev*100:.1f}% → {curr*100:.1f}% (Δ={delta*100:.1f}%)")
            return True
        else:
            print(f"   ✅ [STABLE] {model_id}: {prev*100:.1f}% → {curr*100:.1f}% (Δ={delta*100:.1f}%)")
            return False


if __name__ == "__main__":
    evaluator = OmniModelEvaluator()
    
    test_suite = [
        {"input": "Hitung 2+2", "expected_pass": True},
        {"input": "Jelaskan teori relativitas umum Einstein dalam konteks kosmologi modern", "expected_pass": False},
        {"input": "Apa warna langit?", "expected_pass": True},
        {"input": "Rancang arsitektur microservices untuk platform e-commerce skala enterprise", "expected_pass": False},
    ]
    
    evaluator.evaluate_model("omni-nano-2b", test_suite)
    evaluator.evaluate_model("omni-nano-2b", test_suite[:2])  # Skor turun
    evaluator.detect_drift("omni-nano-2b")
