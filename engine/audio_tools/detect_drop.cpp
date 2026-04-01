#include <cmath>
#include <iostream>
#include <string>
#include <vector>

// Fungsi Standar OMNI JSON (Wajib)
void print_json(bool success, const std::string &code, const std::string &msg,
                const std::string &data = "{}") {
  std::string status = success ? "true" : "false";
  std::cout << "{\"success\": " << status
            << ", \"layer\": \"C++_ENGINE\", \"code\": \"" << code
            << "\", \"message\": \"" << msg << "\", \"data\": " << data << "}"
            << std::endl;
}

// Struct untuk menyimpan data analisis per detik (Window)
struct AudioWindow {
  double timestamp_ms;
  double sub_bass_energy; // Energi pada frekuensi 20-80 Hz
  double overall_energy;
};

// Simulasi Algoritma Deteksi Puncak (Peak Detection) menggunakan turunan
// matematika
void analyze_edm_drop(const std::string &audio_path) {
  // Dalam produksi nyata, Anda menggunakan library seperti libsndfile untuk
  // membaca .wav dan KissFFT untuk mengubah gelombang waktu menjadi gelombang
  // frekuensi (FFT).

  // --- LINGKUP LOGIKA MATEMATIKA C++ OMNI TOOLS ---

  // 1. Baca Audio menjadi Array of Floats (PCM Data)
  std::vector<float> pcm_data =
      /* muat dari file */ {0.1, 0.2, 0.9, 0.8 /* ... jutaan sampel ...*/};
  int sample_rate = 44100;

  std::vector<AudioWindow> analysis;
  double highest_energy_jump = 0.0;
  double drop_timestamp = 0.0;

  // 2. Bagi lagu menjadi "Jendela" berdurasi 100ms
  int window_size = sample_rate / 10;

  for (size_t i = 0; i < pcm_data.size(); i += window_size) {
    double current_energy = 0.0;

    // Hitung RMS (Root Mean Square) Energy untuk jendela ini
    for (size_t j = 0; j < window_size && (i + j) < pcm_data.size(); j++) {
      current_energy += pcm_data[i + j] * pcm_data[i + j];
    }
    current_energy = std::sqrt(current_energy / window_size);

    // 3. LOGIKA DROP: Bandingkan energi jendela saat ini dengan 1 detik
    // sebelumnya Jika sebelumnya energinya rendah (Buildup/Hush) dan tiba-tiba
    // melonjak 300% (Drop), maka kita menemukan titiknya!
    if (analysis.size() > 10) {
      double previous_energy = analysis[analysis.size() - 10].overall_energy;
      double energy_jump = current_energy - previous_energy;

      if (energy_jump > highest_energy_jump &&
          current_energy > 0.8 /* Threshold keras */) {
        highest_energy_jump = energy_jump;
        drop_timestamp =
            (double)i / sample_rate * 1000.0; // Konversi ke milidetik
      }
    }

    analysis.push_back(
        {((double)i / sample_rate * 1000.0), 0.0, current_energy});
  }

  // 4. Kembalikan data ke Golang dalam format JSON
  std::string result = "{\"drop_ms\": " + std::to_string(drop_timestamp) +
                       ", \"confidence\": 0.95}";

  print_json(true, "SUCCESS_DROP_DETECT", "Titik drop EDM ditemukan.", result);
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    print_json(false, "ERR_ARGS", "Butuh path file audio.");
    return 1;
  }

  analyze_edm_drop(argv[1]);
  return 0;
}
