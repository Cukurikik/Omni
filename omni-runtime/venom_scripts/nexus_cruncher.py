# ==========================================
# 🐍 OMNI-NEXUS: API DATA CRUNCHER
# ==========================================
# Pipeline: Golang HTTP → Rust Validate → Python Crunch → TypeScript UI
#
# File ini dieksekusi langsung di dalam RAM Golang melalui
# CPython bridge (Venom Engine). TIDAK ADA Flask/Uvicorn!
#
# Lokasi: venom_scripts/nexus_cruncher.py
# Panggil dari TypeScript:
#   const data = await omniFetch("https://api.crypto.com/btc", {
#       usePythonCruncher: { script: "nexus_cruncher", func: "proses_data_kripto" }
#   });
# ==========================================

import json
import math
from datetime import datetime


# ==========================================
# 💰 CRYPTO DATA PROCESSOR
# ==========================================

def proses_data_kripto(payload):
    """
    ⚡ Memproses data kripto raksasa (10.000+ data points).
    Menghitung statistik komprehensif tanpa Pandas.
    Pure Python math — zero external dependencies!
    """
    print(f"🐍 [NEXUS-PYTHON] Memproses data kripto... [{datetime.now().isoformat()}]")

    if isinstance(payload, str):
        payload = json.loads(payload)

    # Coba ekstrak data dari berbagai format API
    data = None
    if isinstance(payload, list):
        data = payload
    elif isinstance(payload, dict):
        # CoinGecko format
        if "prices" in payload:
            data = [p[1] if isinstance(p, list) else p for p in payload["prices"]]
        # Binance format
        elif "data" in payload and isinstance(payload["data"], list):
            data = payload["data"]
        # Generic format
        elif "harga_bitcoin" in payload:
            data = [item.get("price", item) if isinstance(item, dict) else item
                    for item in payload["harga_bitcoin"]]
        # Flat number array
        elif "values" in payload:
            data = payload["values"]

    if not data:
        return json.dumps({"error": "Format data tidak dikenali oleh Nexus Cruncher"})

    # Filter hanya angka
    numbers = [float(x) for x in data if isinstance(x, (int, float))]
    n = len(numbers)

    if n == 0:
        return json.dumps({"error": "Tidak ada data numerik"})

    # ==========================================
    # STATISTIK KOMPREHENSIF
    # ==========================================
    mean = sum(numbers) / n
    sorted_nums = sorted(numbers)

    # Median
    if n % 2 == 1:
        median = sorted_nums[n // 2]
    else:
        median = (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2

    # Variance & Std Dev
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std = math.sqrt(variance)

    # Quartiles (Q1, Q3, IQR)
    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_nums[q1_idx]
    q3 = sorted_nums[q3_idx]
    iqr = q3 - q1

    # Skewness
    if std > 0:
        skewness = sum(((x - mean) / std) ** 3 for x in numbers) / n
    else:
        skewness = 0

    # Kurtosis
    if std > 0:
        kurtosis = sum(((x - mean) / std) ** 4 for x in numbers) / n - 3
    else:
        kurtosis = 0

    # Trend Detection
    if n >= 4:
        quarter = n // 4
        first_q = sum(numbers[:quarter]) / quarter
        last_q = sum(numbers[-quarter:]) / quarter
        change_pct = ((last_q - first_q) / first_q * 100) if first_q != 0 else 0
        if change_pct > 5:
            trend = "BULLISH 🚀"
        elif change_pct < -5:
            trend = "BEARISH 📉"
        else:
            trend = "SIDEWAYS ↔️"
    else:
        trend = "insufficient_data"
        change_pct = 0

    # Volatility (Coefficient of Variation)
    volatility = (std / mean * 100) if mean != 0 else 0

    # Moving Average (simple 10-period)
    ma_period = min(10, n)
    ma_10 = sum(numbers[-ma_period:]) / ma_period

    result = {
        "engine": "OMNI-NEXUS Python Cruncher v2.0",
        "timestamp": datetime.now().isoformat(),
        "data_points": n,
        "statistics": {
            "mean": round(mean, 6),
            "median": round(median, 6),
            "std": round(std, 6),
            "variance": round(variance, 6),
            "min": round(min(numbers), 6),
            "max": round(max(numbers), 6),
            "range": round(max(numbers) - min(numbers), 6),
            "q1": round(q1, 6),
            "q3": round(q3, 6),
            "iqr": round(iqr, 6),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4),
        },
        "analysis": {
            "trend": trend,
            "change_pct": round(change_pct, 2),
            "volatility_pct": round(volatility, 2),
            "ma_10": round(ma_10, 6),
            "risk_level": "HIGH" if volatility > 50 else "MEDIUM" if volatility > 20 else "LOW",
        },
    }

    print(f"🐍 [NEXUS-PYTHON] ✅ Analisis selesai: {n} data points, trend={trend}")
    return json.dumps(result)


# ==========================================
# 📊 GENERIC API DATA ANALYZER
# ==========================================

def analyze_api_response(payload):
    """
    Menganalisis response API generik — menghitung statistik,
    menemukan pola, dan memberikan insight.
    """
    print("🐍 [NEXUS-PYTHON] Menganalisis API response...")

    if isinstance(payload, str):
        payload = json.loads(payload)

    # Analisis struktur
    analysis = {
        "engine": "OMNI-NEXUS API Analyzer",
        "structure": describe_structure(payload),
        "timestamp": datetime.now().isoformat(),
    }

    # Jika ada data numerik, hitung statistik
    numbers = extract_numbers(payload)
    if numbers:
        n = len(numbers)
        mean = sum(numbers) / n
        analysis["numeric_stats"] = {
            "count": n,
            "sum": round(sum(numbers), 4),
            "mean": round(mean, 4),
            "min": round(min(numbers), 4),
            "max": round(max(numbers), 4),
        }

    # Hitung string lengths
    strings = extract_strings(payload)
    if strings:
        analysis["text_stats"] = {
            "string_count": len(strings),
            "avg_length": round(sum(len(s) for s in strings) / len(strings), 1),
            "max_length": max(len(s) for s in strings),
            "unique_count": len(set(strings)),
        }

    return json.dumps(analysis)


# ==========================================
# 🔮 PREDICTION ENGINE
# ==========================================

def predict_next_values(payload):
    """
    Prediksi nilai berikutnya menggunakan Linear Regression + Exponential Smoothing.
    Pure math — zero dependencies!
    """
    print("🐍 [NEXUS-PYTHON] Menjalankan mesin prediksi...")

    if isinstance(payload, str):
        payload = json.loads(payload)

    data = payload.get("data", payload.get("values", []))
    periods = payload.get("periods", 5)

    if len(data) < 3:
        return json.dumps({"error": "Butuh minimal 3 data points untuk prediksi"})

    numbers = [float(x) for x in data if isinstance(x, (int, float))]
    n = len(numbers)

    # Linear Regression: y = mx + b
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(numbers) / n

    num = sum((x[i] - x_mean) * (numbers[i] - y_mean) for i in range(n))
    den = sum((x[i] - x_mean) ** 2 for i in range(n))

    if den == 0:
        return json.dumps({"error": "Varians nol — tidak bisa regresi"})

    slope = num / den
    intercept = y_mean - slope * x_mean

    # R-squared
    ss_res = sum((numbers[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
    ss_tot = sum((numbers[i] - y_mean) ** 2 for i in range(n))
    r_sq = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

    # Predictions
    linear_preds = [round(slope * (n + i) + intercept, 4) for i in range(periods)]

    # Exponential Smoothing (alpha=0.3)
    alpha = 0.3
    smoothed = [numbers[0]]
    for i in range(1, n):
        smoothed.append(alpha * numbers[i] + (1 - alpha) * smoothed[-1])
    exp_preds = [round(smoothed[-1], 4)] * periods  # Flat forecast

    result = {
        "engine": "OMNI-NEXUS Prediction Engine",
        "model": "Linear Regression + Exponential Smoothing",
        "input_size": n,
        "predictions": {
            "linear": linear_preds,
            "exponential_smooth": exp_preds,
        },
        "regression": {
            "slope": round(slope, 6),
            "intercept": round(intercept, 6),
            "r_squared": round(r_sq, 4),
            "confidence": "HIGH" if r_sq > 0.8 else "MEDIUM" if r_sq > 0.5 else "LOW",
        },
        "recommendation": "BUY" if slope > 0 and r_sq > 0.5 else "SELL" if slope < 0 and r_sq > 0.5 else "HOLD",
    }

    return json.dumps(result)


# ==========================================
# 🔧 HELPER FUNCTIONS
# ==========================================

def describe_structure(obj, depth=0, max_depth=3):
    """Describe JSON structure recursively."""
    if depth >= max_depth:
        return "..."
    if isinstance(obj, dict):
        return {k: describe_structure(v, depth + 1) for k, v in list(obj.items())[:20]}
    elif isinstance(obj, list):
        if len(obj) == 0:
            return "[]"
        return f"[{type(obj[0]).__name__} x {len(obj)}]"
    elif isinstance(obj, (int, float)):
        return "number"
    elif isinstance(obj, str):
        return f"string({len(obj)})"
    elif isinstance(obj, bool):
        return "boolean"
    elif obj is None:
        return "null"
    return type(obj).__name__


def extract_numbers(obj, result=None):
    """Recursively extract all numbers from nested structure."""
    if result is None:
        result = []
    if isinstance(obj, (int, float)) and not isinstance(obj, bool):
        result.append(float(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            extract_numbers(v, result)
    elif isinstance(obj, list):
        for item in obj:
            extract_numbers(item, result)
    return result


def extract_strings(obj, result=None):
    """Recursively extract all strings from nested structure."""
    if result is None:
        result = []
    if isinstance(obj, str):
        result.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            extract_strings(v, result)
    elif isinstance(obj, list):
        for item in obj:
            extract_strings(item, result)
    return result
