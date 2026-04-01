// ==========================================
// 🧠 OMNI MANIPULATOR: MEMORY-MAPPED FILE ENGINE
// ==========================================
// Memanipulasi file raksasa (50GB+) menggunakan mmap.
// OS memetakan file SSD ke Virtual Address Space — C++ merasa
// punya RAM 50GB padahal OS membaca dari SSD secuil demi secuil.
//
// Penggunaan:
//   omni_manipulator <command> <input_path> [output_path] [args...]
//
// Commands:
//   info       - Tampilkan informasi file (ukuran, magic bytes)
//   xor_crypt  - Enkripsi/dekripsi XOR sederhana (reversible)
//   search     - Cari pattern bytes dalam file raksasa
//   patch      - Ganti bytes di offset tertentu
// ==========================================

#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>

// Cross-platform mmap support
#ifdef _WIN32
#include <io.h>
#include <windows.h>
#else
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#endif

// ==========================================
// CROSS-PLATFORM MMAP WRAPPER
// ==========================================
struct MappedFile {
  char *data;
  size_t size;
  bool writable;

#ifdef _WIN32
  HANDLE fileHandle;
  HANDLE mapHandle;
#else
  int fd;
#endif
};

MappedFile mmapOpen(const char *filepath, bool writable) {
  MappedFile mf = {};
  mf.writable = writable;

#ifdef _WIN32
  DWORD access = writable ? GENERIC_READ | GENERIC_WRITE : GENERIC_READ;
  DWORD shareMode = FILE_SHARE_READ;
  mf.fileHandle = CreateFileA(filepath, access, shareMode, NULL, OPEN_EXISTING,
                              FILE_ATTRIBUTE_NORMAL, NULL);

  if (mf.fileHandle == INVALID_HANDLE_VALUE) {
    std::cerr << "Gagal membuka file: " << filepath << std::endl;
    return mf;
  }

  LARGE_INTEGER fileSize;
  GetFileSizeEx(mf.fileHandle, &fileSize);
  mf.size = static_cast<size_t>(fileSize.QuadPart);

  DWORD flProtect = writable ? PAGE_READWRITE : PAGE_READONLY;
  mf.mapHandle = CreateFileMappingA(mf.fileHandle, NULL, flProtect, 0, 0, NULL);

  if (!mf.mapHandle) {
    std::cerr << "CreateFileMapping gagal!" << std::endl;
    CloseHandle(mf.fileHandle);
    mf.data = nullptr;
    return mf;
  }

  DWORD mapAccess = writable ? FILE_MAP_WRITE : FILE_MAP_READ;
  mf.data =
      static_cast<char *>(MapViewOfFile(mf.mapHandle, mapAccess, 0, 0, 0));

  if (!mf.data) {
    std::cerr << "MapViewOfFile gagal!" << std::endl;
    CloseHandle(mf.mapHandle);
    CloseHandle(mf.fileHandle);
    return mf;
  }
#else
  int flags = writable ? O_RDWR : O_RDONLY;
  mf.fd = open(filepath, flags);

  if (mf.fd == -1) {
    std::cerr << "Gagal membuka file: " << filepath << std::endl;
    return mf;
  }

  struct stat sb;
  fstat(mf.fd, &sb);
  mf.size = sb.st_size;

  int prot = writable ? (PROT_READ | PROT_WRITE) : PROT_READ;
  mf.data =
      static_cast<char *>(mmap(NULL, mf.size, prot, MAP_SHARED, mf.fd, 0));

  if (mf.data == MAP_FAILED) {
    std::cerr << "mmap gagal!" << std::endl;
    close(mf.fd);
    mf.data = nullptr;
    return mf;
  }
#endif

  return mf;
}

void mmapClose(MappedFile &mf) {
  if (!mf.data)
    return;

#ifdef _WIN32
  UnmapViewOfFile(mf.data);
  CloseHandle(mf.mapHandle);
  CloseHandle(mf.fileHandle);
#else
  munmap(mf.data, mf.size);
  close(mf.fd);
#endif

  mf.data = nullptr;
}

// ==========================================
// COMMAND: info — Informasi file
// ==========================================
void cmdInfo(MappedFile &mf, const char *path) {
  std::cout << "==========================================\n";
  std::cout << "🧠 OMNI MANIPULATOR — File Info\n";
  std::cout << "==========================================\n";
  std::cout << "📁 Path  : " << path << "\n";
  std::cout << "📊 Size  : " << mf.size << " bytes ";

  if (mf.size >= (1ULL << 30))
    std::cout << "(" << (mf.size / (1ULL << 30)) << " GB)\n";
  else if (mf.size >= (1ULL << 20))
    std::cout << "(" << (mf.size / (1ULL << 20)) << " MB)\n";
  else
    std::cout << "(" << (mf.size / 1024) << " KB)\n";

  // Magic bytes (first 16 bytes)
  std::cout << "🔮 Magic : ";
  size_t showLen = (mf.size < 16) ? mf.size : 16;
  for (size_t i = 0; i < showLen; i++) {
    printf("%02X ", (unsigned char)mf.data[i]);
  }
  std::cout << "\n==========================================\n";
}

// ==========================================
// COMMAND: xor_crypt — XOR Enkripsi/Dekripsi
// ==========================================
void cmdXorCrypt(MappedFile &mf, const char *key) {
  if (!mf.writable) {
    std::cerr << "❌ File harus dibuka dalam mode WRITE untuk enkripsi!\n";
    return;
  }

  size_t keyLen = strlen(key);
  if (keyLen == 0) {
    std::cerr << "❌ Kunci enkripsi tidak boleh kosong!\n";
    return;
  }

  std::cout << "🔐 Memproses XOR pada " << mf.size << " bytes...\n";

  // Proses per-chunk 64MB untuk progress reporting
  const size_t chunkSize = 64 * 1024 * 1024; // 64MB
  size_t processed = 0;

  while (processed < mf.size) {
    size_t end = processed + chunkSize;
    if (end > mf.size)
      end = mf.size;

    for (size_t i = processed; i < end; i++) {
      mf.data[i] ^= key[i % keyLen];
    }

    processed = end;
    int pct = static_cast<int>((double)processed / mf.size * 100);
    std::cout << "\r🔐 Progress: " << pct << "% (" << (processed / (1024 * 1024))
              << " MB)" << std::flush;
  }
  std::cout << "\n✅ XOR selesai. File dimodifikasi secara in-place.\n";
}

// ==========================================
// COMMAND: search — Cari pattern di file raksasa
// ==========================================
void cmdSearch(MappedFile &mf, const char *pattern) {
  size_t patLen = strlen(pattern);
  if (patLen == 0 || patLen > mf.size) {
    std::cerr << "❌ Pattern tidak valid!\n";
    return;
  }

  std::cout << "🔍 Mencari '" << pattern << "' dalam "
            << (mf.size / (1024 * 1024)) << " MB...\n";

  int found = 0;
  for (size_t i = 0; i <= mf.size - patLen; i++) {
    if (memcmp(mf.data + i, pattern, patLen) == 0) {
      found++;
      std::cout << "   📍 Ditemukan di offset " << i << " (0x" << std::hex << i
                << std::dec << ")\n";
      if (found >= 100) {
        std::cout << "   ... (terpotong pada 100 hasil)\n";
        break;
      }
    }
  }

  if (found == 0) {
    std::cout << "   ❌ Pattern tidak ditemukan.\n";
  } else {
    std::cout << "✅ Total ditemukan: " << found << " lokasi.\n";
  }
}

// ==========================================
// COMMAND: patch — Ganti bytes di offset tertentu
// ==========================================
void cmdPatch(MappedFile &mf, size_t offset, const char *newBytes) {
  if (!mf.writable) {
    std::cerr << "❌ File harus dibuka dalam mode WRITE untuk patch!\n";
    return;
  }

  size_t patchLen = strlen(newBytes);
  if (offset + patchLen > mf.size) {
    std::cerr << "❌ Offset + panjang patch melebihi ukuran file!\n";
    return;
  }

  memcpy(mf.data + offset, newBytes, patchLen);
  std::cout << "✅ Patch berhasil: " << patchLen << " bytes ditulis di offset "
            << offset << "\n";
}

// ==========================================
// MAIN ENTRY POINT
// ==========================================
int main(int argc, char *argv[]) {
  if (argc < 3) {
    std::cout << "🧠 OMNI MANIPULATOR — Penggunaan:\n";
    std::cout << "   omni_manipulator info <file>\n";
    std::cout << "   omni_manipulator xor_crypt <file> <key>\n";
    std::cout << "   omni_manipulator search <file> <pattern>\n";
    std::cout << "   omni_manipulator patch <file> <offset> <bytes>\n";
    return 1;
  }

  std::string command = argv[1];
  const char *filepath = argv[2];
  bool needWrite = (command == "xor_crypt" || command == "patch");

  MappedFile mf = mmapOpen(filepath, needWrite);
  if (!mf.data) {
    std::cerr << "❌ Gagal membuka file dengan mmap!\n";
    return 1;
  }

  if (command == "info") {
    cmdInfo(mf, filepath);
  } else if (command == "xor_crypt") {
    if (argc < 4) {
      std::cerr << "❌ Kunci enkripsi diperlukan!\n";
      mmapClose(mf);
      return 1;
    }
    cmdXorCrypt(mf, argv[3]);
  } else if (command == "search") {
    if (argc < 4) {
      std::cerr << "❌ Pattern pencarian diperlukan!\n";
      mmapClose(mf);
      return 1;
    }
    cmdSearch(mf, argv[3]);
  } else if (command == "patch") {
    if (argc < 5) {
      std::cerr << "❌ Offset dan bytes diperlukan!\n";
      mmapClose(mf);
      return 1;
    }
    size_t offset = std::stoull(argv[3]);
    cmdPatch(mf, offset, argv[4]);
  } else {
    std::cerr << "❌ Perintah tidak dikenal: " << command << "\n";
  }

  mmapClose(mf);
  return 0;
}
