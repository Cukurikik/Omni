// ============================================================
// ⚙️ OMNI-FS-CORE: C++ RAII File Guard & Template I/O
// ============================================================
// Menggunakan paradigma RAII (Resource Acquisition Is
// Initialization) untuk menjamin file descriptor SELALU
// ditutup saat keluar dari scope — mencegah resource leak
// yang merupakan penyakit kronis di Node.js native addons.
// ============================================================

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <string>
#include <vector>
#include <memory>
#include <stdexcept>

namespace omni {
namespace fs {

// ============================================================
// FileGuard: RAII Wrapper untuk FILE* descriptor
// ============================================================

class FileGuard {
public:
    /// Membuka file dengan mode tertentu ("r", "w", "rb", "wb", dll)
    explicit FileGuard(const char* path, const char* mode)
        : file_(std::fopen(path, mode))
        , path_(path ? path : "")
    {
        if (!file_) {
            throw std::runtime_error(
                std::string("omni-fs: Gagal membuka '") + path_ + 
                "': " + std::strerror(errno)
            );
        }
    }

    /// Destruktor: otomatis menutup file saat keluar scope
    ~FileGuard() {
        if (file_) {
            std::fclose(file_);
            file_ = nullptr;
        }
    }

    // Non-copyable (mencegah double-free)
    FileGuard(const FileGuard&) = delete;
    FileGuard& operator=(const FileGuard&) = delete;

    // Move-able
    FileGuard(FileGuard&& other) noexcept
        : file_(other.file_), path_(std::move(other.path_))
    {
        other.file_ = nullptr;
    }

    FileGuard& operator=(FileGuard&& other) noexcept {
        if (this != &other) {
            if (file_) std::fclose(file_);
            file_ = other.file_;
            path_ = std::move(other.path_);
            other.file_ = nullptr;
        }
        return *this;
    }

    /// Akses raw FILE* pointer (untuk operasi stdio)
    FILE* get() const { return file_; }

    /// Membaca seluruh isi file ke buffer
    std::vector<char> read_all() {
        std::fseek(file_, 0, SEEK_END);
        long size = std::ftell(file_);
        std::fseek(file_, 0, SEEK_SET);

        if (size <= 0) return {};

        std::vector<char> buffer(static_cast<size_t>(size));
        size_t read_count = std::fread(buffer.data(), 1, buffer.size(), file_);
        buffer.resize(read_count);
        return buffer;
    }

    /// Menulis data ke file
    size_t write(const void* data, size_t size) {
        return std::fwrite(data, 1, size, file_);
    }

    /// Menulis string ke file
    size_t write_string(const std::string& str) {
        return write(str.data(), str.size());
    }

    /// Path file yang sedang dibuka
    const std::string& path() const { return path_; }

private:
    FILE*       file_;
    std::string path_;
};

// ============================================================
// FileReader<N>: Template dengan compile-time buffer sizing
// ============================================================

template<size_t BufferSize = 4096>
class FileReader {
public:
    explicit FileReader(const char* path)
        : guard_(path, "rb")
        , bytes_read_(0)
    {}

    /// Membaca chunk berikutnya ke dalam internal buffer.
    /// Mengembalikan jumlah byte yang dibaca (0 = EOF).
    size_t read_chunk() {
        bytes_read_ = std::fread(buffer_, 1, BufferSize, guard_.get());
        return bytes_read_;
    }

    /// Pointer ke data buffer internal
    const char* data() const { return buffer_; }

    /// Jumlah byte terakhir yang berhasil dibaca
    size_t last_read_size() const { return bytes_read_; }

    /// Membaca seluruh file sebagai string
    std::string read_to_string() {
        std::string result;
        while (read_chunk() > 0) {
            result.append(buffer_, bytes_read_);
        }
        return result;
    }

private:
    FileGuard guard_;
    char      buffer_[BufferSize];
    size_t    bytes_read_;
};

// ============================================================
// Utility Functions (C-linkage untuk interop FFI OMNI)
// ============================================================

extern "C" {
    /// Membaca seluruh file dan mengembalikan buffer baru.
    /// Caller HARUS memanggil free() pada hasil.
    char* omni_cpp_read_file(const char* path, size_t* out_size) {
        try {
            FileGuard fg(path, "rb");
            auto data = fg.read_all();
            
            char* result = static_cast<char*>(std::malloc(data.size() + 1));
            if (!result) return nullptr;
            
            std::memcpy(result, data.data(), data.size());
            result[data.size()] = '\0';
            *out_size = data.size();
            return result;
        } catch (...) {
            *out_size = 0;
            return nullptr;
        }
    }

    /// Menulis data ke file menggunakan RAII guard.
    int omni_cpp_write_file(const char* path, const char* data, size_t len) {
        try {
            FileGuard fg(path, "wb");
            size_t written = fg.write(data, len);
            return (written == len) ? 0 : -1;
        } catch (...) {
            return -1;
        }
    }
}

} // namespace fs
} // namespace omni
