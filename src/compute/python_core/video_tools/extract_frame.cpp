#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>

// Fungsi Standar OMNI JSON (Wajib)
void print_json(bool success, const std::string &code, const std::string &msg,
                const std::string &data = "{}") {
  std::string status = success ? "true" : "false";
  std::cout << "{\"success\": " << status
            << ", \"layer\": \"C++_ENGINE\", \"code\": \"" << code
            << "\", \"message\": \"" << msg << "\", \"data\": " << data << "}"
            << std::endl;
}

int main(int argc, char *argv[]) {
  // Argumen dari Golang: [1] path_video_karantina [2] timestamp_ms [3]
  // output_hash
  if (argc < 4) {
    print_json(false, "ERR_ARGS",
               "Parameter tidak lengkap untuk ekstraksi video.");
    return 1;
  }

  std::string input_video = argv[1];
  double target_time_ms = std::stod(argv[2]);
  std::string output_path =
      std::string("../release/omni_cache/") + argv[3] + ".jpg";

  // 1. Buka File Video (Tanpa memuat seluruh file ke RAM)
  cv::VideoCapture cap(input_video);
  if (!cap.isOpened()) {
    print_json(false, "ERR_VID_OPEN",
               "Gagal membaca format video dari karantina.");
    return 1;
  }

  // 2. Lompat presisi tinggi (Seek) ke milidetik yang diminta
  cap.set(cv::CAP_PROP_POS_MSEC, target_time_ms);

  // 3. Tarik (Extract) 1 Frame piksel ke memori
  cv::Mat frame;
  cap >> frame;

  if (frame.empty()) {
    print_json(false, "ERR_FRAME_EMPTY",
               "Frame tidak ditemukan di timestamp tersebut.");
    return 1;
  }

  // 4. Kompres dan Simpan ke folder Ephemeral Cache (yang akan dihapus Janitor
  // dalam 1 jam)
  bool is_saved = cv::imwrite(output_path, frame);

  if (is_saved) {
    std::string json_data = "{\"cache_path\": \"" + output_path + "\"}";
    print_json(true, "SUCCESS", "Frame berhasil diekstrak.", json_data);
  } else {
    print_json(false, "ERR_SAVE", "Gagal menulis file ke omni_cache.");
  }

  return 0; // C++ Engine mati, RAM kembali bersih 100%
}
