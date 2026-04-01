#include <fcntl.h>
#include <iostream>
#include <string>
#include <sys/stat.h>

// Catatan OS: Untuk Windows native (MSVC/MinGW standar tanpa POSIX wrapper),
// gunakan <windows.h> CreateFileMapping/MapViewOfFile.
// Jika menggunakan WSL atau Cygwin/MSYS2 dengan POSIX support, <sys/mman.h>
// bisa digunakan.
#ifdef _WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

// Fungsi cetak JSON Universal
void print_json(bool success, const std::string &code, const std::string &msg,
                const std::string &data = "{}") {
  std::string status = success ? "true" : "false";
  std::cout << "{\"success\": " << status
            << ", \"layer\": \"C++_MMAP_ENGINE\", \"code\": \"" << code
            << "\", \"message\": \"" << msg << "\", \"data\": " << data << "}"
            << std::endl;
}

void process_audio_zero_copy(const char *file_path) {
#ifdef _WIN32
  // Windows Native MMAP Implementation
  HANDLE hFile = CreateFileA(file_path, GENERIC_READ, FILE_SHARE_READ, NULL,
                             OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
  if (hFile == INVALID_HANDLE_VALUE) {
    print_json(false, "ERR_FD_OPEN", "Gagal membuka file dari karantina.");
    return;
  }

  LARGE_INTEGER fileSize;
  if (!GetFileSizeEx(hFile, &fileSize)) {
    CloseHandle(hFile);
    print_json(false, "ERR_FSTAT", "Gagal membaca struktur ukuran file.");
    return;
  }

  HANDLE hMapping = CreateFileMappingA(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
  if (hMapping == NULL) {
    CloseHandle(hFile);
    print_json(false, "ERR_MMAP", "OS menolak Memory-Mapping untuk file ini.");
    return;
  }

  char *mapped_memory =
      static_cast<char *>(MapViewOfFile(hMapping, FILE_MAP_READ, 0, 0, 0));
  if (mapped_memory == NULL) {
    CloseHandle(hMapping);
    CloseHandle(hFile);
    print_json(false, "ERR_MMAP_VIEW", "Gagal memetakan view dari file.");
    return;
  }

  long long st_size = fileSize.QuadPart;
#else
  // POSIX Native MMAP Implementation
  int fd = open(file_path, O_RDONLY);
  if (fd == -1) {
    print_json(false, "ERR_FD_OPEN",
               "Gagal membuka file descriptor dari karantina.");
    return;
  }

  struct stat sb;
  if (fstat(fd, &sb) == -1) {
    close(fd);
    print_json(false, "ERR_FSTAT", "Gagal membaca struktur ukuran file.");
    return;
  }

  char *mapped_memory = static_cast<char *>(
      mmap(nullptr, sb.st_size, PROT_READ, MAP_PRIVATE, fd, 0));

  if (mapped_memory == MAP_FAILED) {
    close(fd);
    print_json(false, "ERR_MMAP", "OS menolak Memory-Mapping untuk file ini.");
    return;
  }

  long long st_size = sb.st_size;
#endif

  // ==============================================================
  // 3. PROSES DATA SECARA INSTAN! (ZERO-COPY)
  // ==============================================================
  double simulated_drop_ms = 0.0;

  if (st_size > 1000) {
    char sample_byte = mapped_memory[st_size / 2];
    simulated_drop_ms = static_cast<double>(sample_byte) * 100.0;
  }

  // ==============================================================
  // 4. PEMBEBASAN MEMORI YANG ELEGAN
  // ==============================================================
#ifdef _WIN32
  UnmapViewOfFile(mapped_memory);
  CloseHandle(hMapping);
  CloseHandle(hFile);
#else
  if (munmap(mapped_memory, st_size) == -1) {
    print_json(false, "ERR_MUNMAP",
               "Gagal melepaskan pemetaan memori. Waspada RAM Leak!");
    close(fd);
    return;
  }
  close(fd);
#endif

  std::string result_data =
      "{\"drop_ms\": " + std::to_string(simulated_drop_ms) + "}";
  print_json(true, "SUCCESS_MMAP",
             "Pemrosesan Zero-Copy berhasil dalam hitungan milidetik.",
             result_data);
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    print_json(false, "ERR_ARGS", "Engine butuh path file karantina.");
    return 1;
  }

  process_audio_zero_copy(argv[1]);
  return 0;
}
