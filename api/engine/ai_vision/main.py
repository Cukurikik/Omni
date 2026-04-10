import sys
import json
import cv2
import os

def process_vision(job):
    try:
        input_path = job.get("input_path")
        output_path = job.get("output_path")

        # 1. Validasi File dari SSD (Dikirim oleh Golang)
        if not os.path.exists(input_path):
            return {"status": "FAILED", "error": "File gambar tidak ditemukan di SSD."}

        # 2. Buka gambar menggunakan mesin C++ OpenCV di dalam Python
        img = cv2.imread(input_path)
        if img is None:
            return {"status": "FAILED", "error": "Format gambar tidak dapat dibaca oleh OpenCV."}

        # 3. KECERDASAN BUATAN (AI VISION): Deteksi Tepi (Edge Detection) & Grayscale
        # Ini akan mengubah foto biasa menjadi sketsa digital beresolusi tinggi!
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)

        # 4. Simpan hasil ke SSD
        cv2.imwrite(output_path, edges)

        # 5. Laporkan kesuksesan ke Jenderal Golang
        return {
            "status": "COMPLETED", 
            "job_id": job.get("id"), 
            "message": "AI Vision berhasil memetakan struktur piksel."
        }
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

if __name__ == "__main__":
    # ⚡ PROTOKOL OMNI-POLYGLOT: Membaca perintah langsung dari memori Golang!
    raw_input = sys.stdin.read()
    job_data = json.loads(raw_input)

    # Eksekusi AI dan kembalikan laporan via Terminal Output
    result = process_vision(job_data)
    print(json.dumps(result))