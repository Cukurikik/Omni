# ==========================================
# 🐍 OMNI-VENOM: CONTOH DATA CRUNCHER
# ==========================================
# File ini adalah contoh script Python yang bisa dipanggil
# langsung dari TypeScript tanpa Flask/FastAPI!
#
# Lokasi: venom_scripts/data_cruncher.py
# Panggil dari TypeScript:
#   import { runVenom } from 'omni/python';
#   const result = runVenom("data_cruncher", "proses_big_data", data);
# ==========================================

import json
import math


def proses_big_data(payload):
    """
    ⚡ Memproses data besar langsung di RAM Golang!
    Tidak perlu API Flask. Tidak ada HTTP overhead.
    
    Args:
        payload: dict dari TypeScript (auto-parsed dari JSON)
    
    Returns:
        JSON string dengan hasil analisis statistik
    """
    print("🐍 [VENOM] Menerima data dari TypeScript via Golang...")
    
    # Ekstrak data
    if isinstance(payload, str):
        payload = json.loads(payload)
    
    data = payload.get("sales", [])
    region = payload.get("region", "Unknown")
    
    if not data:
        return json.dumps({"error": "Data kosong"})
    
    # Statistik dasar (tanpa NumPy — zero dependencies!)
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std = math.sqrt(variance)
    minimum = min(data)
    maximum = max(data)
    sorted_data = sorted(data)
    median = sorted_data[n // 2] if n % 2 == 1 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    
    # Trend detection
    if len(data) >= 2:
        first_half = sum(data[:n//2]) / (n//2)
        second_half = sum(data[n//2:]) / (n - n//2)
        trend = "naik" if second_half > first_half else "turun" if second_half < first_half else "stabil"
    else:
        trend = "insufficient_data"
    
    result = {
        "region": region,
        "count": n,
        "mean": round(mean, 2),
        "median": median,
        "std": round(std, 2),
        "min": minimum,
        "max": maximum,
        "trend": trend,
        "engine": "OMNI-VENOM (Native CPython)",
    }
    
    print(f"🐍 [VENOM] Analisis selesai: {n} data points, trend={trend}")
    
    return json.dumps(result)


def predict_sales(payload):
    """
    Prediksi penjualan menggunakan Simple Linear Regression.
    Tanpa scikit-learn — pure Python math!
    """
    if isinstance(payload, str):
        payload = json.loads(payload)
    
    data = payload.get("historical", [])
    periods_ahead = payload.get("periods", 3)
    
    if len(data) < 2:
        return json.dumps({"error": "Butuh minimal 2 data points"})
    
    n = len(data)
    x = list(range(n))
    y = data
    
    # Linear Regression: y = mx + b
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        return json.dumps({"error": "Tidak bisa menghitung regresi (varians nol)"})
    
    m = numerator / denominator
    b = y_mean - m * x_mean
    
    # Predict
    predictions = [round(m * (n + i) + b, 2) for i in range(periods_ahead)]
    
    # R-squared
    ss_res = sum((y[i] - (m * x[i] + b)) ** 2 for i in range(n))
    ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    return json.dumps({
        "predictions": predictions,
        "slope": round(m, 4),
        "intercept": round(b, 4),
        "r_squared": round(r_squared, 4),
        "confidence": "high" if r_squared > 0.8 else "medium" if r_squared > 0.5 else "low",
        "engine": "OMNI-VENOM Linear Regression",
    })


def classify_text(payload):
    """
    Klasifikasi sentimen teks sederhana.
    Pure Python — tanpa NLTK/transformers!
    """
    if isinstance(payload, str):
        payload = json.loads(payload)
    
    text = payload.get("text", "").lower()
    
    positive_words = {"good", "great", "excellent", "amazing", "wonderful", "fantastic",
                      "awesome", "love", "happy", "best", "perfect", "beautiful",
                      "bagus", "hebat", "luar biasa", "senang", "bahagia", "sempurna"}
    negative_words = {"bad", "terrible", "awful", "horrible", "worst", "hate",
                      "ugly", "poor", "sad", "angry", "disappointed", "broken",
                      "jelek", "buruk", "parah", "kecewa", "marah", "rusak"}
    
    words = text.split()
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    total = pos_count + neg_count
    if total == 0:
        sentiment = "neutral"
        confidence = 0.5
    elif pos_count > neg_count:
        sentiment = "positive"
        confidence = pos_count / total
    else:
        sentiment = "negative"
        confidence = neg_count / total
    
    return json.dumps({
        "text": text[:100],
        "sentiment": sentiment,
        "confidence": round(confidence, 2),
        "positive_hits": pos_count,
        "negative_hits": neg_count,
        "engine": "OMNI-VENOM Sentiment Analyzer",
    })
