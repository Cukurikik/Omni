/* ============================================================
 * 🔧 OMNI-FS-CORE: C POSIX Syscall Layer
 * ============================================================
 * Akses langsung ke kernel I/O tanpa abstraksi VM.
 * File ini di-compile oleh OMNI Build Toolchain menggunakan
 * `cc` (gcc/clang) dan di-link sebagai object file `.o`
 * ke dalam binary LLVM akhir.
 *
 * Menggantikan: Node.js `libuv` fs binding (C++)
 * ============================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

/* Platform-specific headers */
#ifdef _WIN32
    #include <io.h>
    #include <fcntl.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #define OMNI_OPEN  _open
    #define OMNI_READ  _read
    #define OMNI_WRITE _write
    #define OMNI_CLOSE _close
    #define OMNI_STAT  _stat
    typedef struct _stat OmniStatBuf;
#else
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/stat.h>
    #include <sys/types.h>
    #define OMNI_OPEN  open
    #define OMNI_READ  read
    #define OMNI_WRITE write
    #define OMNI_CLOSE close
    #define OMNI_STAT  stat
    typedef struct stat OmniStatBuf;
#endif

/* ============================================================
 * Tipe Data FFI (Bisa diakses dari Rust/Go via OMNI Bridge)
 * ============================================================ */

typedef struct {
    int    fd;           /* File descriptor OS */
    int    flags;        /* O_RDONLY, O_WRONLY, O_RDWR */
    size_t position;     /* Posisi kursor baca/tulis */
} OmniFileHandle;

typedef struct {
    size_t   size;       /* Ukuran file dalam bytes */
    int      is_dir;     /* 1 = direktori, 0 = file */
    int      is_symlink; /* 1 = symlink */
    long     mtime;      /* Waktu modifikasi terakhir (epoch) */
    long     ctime;      /* Waktu pembuatan (epoch) */
    int      readonly;   /* 1 = readonly */
} OmniFileStat;

typedef struct {
    int    code;         /* 0 = OK, negatif = error */
    char   message[256]; /* Pesan error (jika ada) */
} OmniResult;

/* ============================================================
 * Fungsi Inti: Membuka File
 * ============================================================ */
OmniFileHandle omni_open(const char* path, int flags) {
    OmniFileHandle handle;
    handle.flags = flags;
    handle.position = 0;
    
    #ifdef _WIN32
        handle.fd = OMNI_OPEN(path, flags | _O_BINARY, _S_IREAD | _S_IWRITE);
    #else
        handle.fd = OMNI_OPEN(path, flags, 0644);
    #endif
    
    return handle;
}

/* ============================================================
 * Fungsi Inti: Membaca Data dari File Descriptor
 * ============================================================ */
int omni_read(OmniFileHandle* handle, void* buffer, size_t count) {
    if (handle->fd < 0) return -1;
    
    int bytes_read = (int)OMNI_READ(handle->fd, buffer, (unsigned int)count);
    if (bytes_read > 0) {
        handle->position += bytes_read;
    }
    return bytes_read;
}

/* ============================================================
 * Fungsi Inti: Menulis Data ke File Descriptor
 * ============================================================ */
int omni_write(OmniFileHandle* handle, const void* buffer, size_t count) {
    if (handle->fd < 0) return -1;
    
    int bytes_written = (int)OMNI_WRITE(handle->fd, buffer, (unsigned int)count);
    if (bytes_written > 0) {
        handle->position += bytes_written;
    }
    return bytes_written;
}

/* ============================================================
 * Fungsi Inti: Menutup File Descriptor
 * ============================================================ */
OmniResult omni_close(OmniFileHandle* handle) {
    OmniResult result;
    result.code = 0;
    memset(result.message, 0, sizeof(result.message));
    
    if (handle->fd >= 0) {
        if (OMNI_CLOSE(handle->fd) != 0) {
            result.code = -errno;
            snprintf(result.message, sizeof(result.message),
                     "Failed to close fd %d: %s", handle->fd, strerror(errno));
        }
        handle->fd = -1;
    }
    return result;
}

/* ============================================================
 * Fungsi Inti: Mengambil Metadata File (stat)
 * ============================================================ */
OmniResult omni_stat(const char* path, OmniFileStat* out) {
    OmniResult result;
    result.code = 0;
    memset(result.message, 0, sizeof(result.message));
    
    OmniStatBuf sb;
    if (OMNI_STAT(path, &sb) != 0) {
        result.code = -errno;
        snprintf(result.message, sizeof(result.message),
                 "stat failed for '%s': %s", path, strerror(errno));
        return result;
    }
    
    out->size = (size_t)sb.st_size;
    #ifdef _WIN32
        out->is_dir = (sb.st_mode & _S_IFDIR) ? 1 : 0;
        out->is_symlink = 0;
        out->readonly = (sb.st_mode & _S_IWRITE) ? 0 : 1;
    #else
        out->is_dir = S_ISDIR(sb.st_mode) ? 1 : 0;
        out->is_symlink = S_ISLNK(sb.st_mode) ? 1 : 0;
        out->readonly = (sb.st_mode & S_IWUSR) ? 0 : 1;
    #endif
    out->mtime = (long)sb.st_mtime;
    out->ctime = (long)sb.st_ctime;
    
    return result;
}

/* ============================================================
 * Fungsi Utilitas: Membaca Seluruh File ke Buffer
 * ============================================================ */
int omni_read_all(const char* path, char** out_buffer, size_t* out_size) {
    OmniFileStat fstat;
    OmniResult res = omni_stat(path, &fstat);
    if (res.code != 0) return res.code;
    
    *out_buffer = (char*)malloc(fstat.size + 1);
    if (*out_buffer == NULL) return -ENOMEM;
    
    #ifdef _WIN32
        OmniFileHandle fh = omni_open(path, _O_RDONLY);
    #else
        OmniFileHandle fh = omni_open(path, O_RDONLY);
    #endif
    if (fh.fd < 0) {
        free(*out_buffer);
        return -errno;
    }
    
    int total = omni_read(&fh, *out_buffer, fstat.size);
    (*out_buffer)[total > 0 ? total : 0] = '\0';
    *out_size = total > 0 ? (size_t)total : 0;
    
    omni_close(&fh);
    return 0;
}

/* ============================================================
 * Fungsi Utilitas: Menulis String ke File (Overwrite)
 * ============================================================ */
int omni_write_all(const char* path, const char* data, size_t len) {
    #ifdef _WIN32
        OmniFileHandle fh = omni_open(path, _O_WRONLY | _O_CREAT | _O_TRUNC);
    #else
        OmniFileHandle fh = omni_open(path, O_WRONLY | O_CREAT | O_TRUNC);
    #endif
    if (fh.fd < 0) return -errno;
    
    int written = omni_write(&fh, data, len);
    omni_close(&fh);
    
    return (written == (int)len) ? 0 : -EIO;
}
