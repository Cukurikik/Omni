/*
 * ==========================================
 * ⚡ OMNI-KINETIC: Native C Hyper-Engine
 * ==========================================
 * Implementasi cross-platform (Windows + Linux)
 *
 * Windows: CreateFileMapping + MapViewOfFile
 * Linux:   mmap + munmap
 *
 * Prinsip: OS memperlakukan SSD seolah-olah itu RAM.
 * File 50GB diproses dengan hanya ~BUFFER_SIZE byte di RAM!
 * ==========================================
 */

#include "kinetic_engine.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ==========================================
 * PLATFORM ABSTRACTION LAYER
 * ========================================== */

#ifdef _WIN32
    /* WINDOWS IMPLEMENTATION */
    #include <windows.h>
    #include <io.h>

    #define KINETIC_BUFFER_SIZE (4 * 1024 * 1024) /* 4MB chunks */

    int kinetic_xor_encrypt(const char* input_path, const char* output_path, unsigned char xor_key) {
        HANDLE hFileIn, hFileOut;
        LARGE_INTEGER fileSize;
        HANDLE hMapIn;
        unsigned char* viewIn;
        DWORD written;
        unsigned char buffer[KINETIC_BUFFER_SIZE];
        LONGLONG offset;
        DWORD chunkSize;
        size_t i;

        /* 1. Buka file input */
        hFileIn = CreateFileA(input_path, GENERIC_READ, FILE_SHARE_READ, NULL,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFileIn == INVALID_HANDLE_VALUE) return KINETIC_ERR_OPEN_IN;

        /* 2. Dapatkan ukuran file */
        GetFileSizeEx(hFileIn, &fileSize);

        /* 3. Buat file output */
        hFileOut = CreateFileA(output_path, GENERIC_WRITE, 0, NULL,
                               CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFileOut == INVALID_HANDLE_VALUE) {
            CloseHandle(hFileIn);
            return KINETIC_ERR_OPEN_OUT;
        }

        /* 4. Buat Memory Map untuk file input */
        hMapIn = CreateFileMappingA(hFileIn, NULL, PAGE_READONLY, 0, 0, NULL);
        if (hMapIn == NULL) {
            CloseHandle(hFileIn);
            CloseHandle(hFileOut);
            return KINETIC_ERR_MAP_FAILED;
        }

        /* 5. KINETIC LOOP: Proses dalam chunk 4MB */
        offset = 0;
        while (offset < fileSize.QuadPart) {
            chunkSize = KINETIC_BUFFER_SIZE;
            if (offset + chunkSize > (DWORD)fileSize.QuadPart) {
                chunkSize = (DWORD)(fileSize.QuadPart - offset);
            }

            /* Map chunk dari file input */
            viewIn = (unsigned char*)MapViewOfFile(hMapIn, FILE_MAP_READ,
                         (DWORD)(offset >> 32), (DWORD)(offset & 0xFFFFFFFF), chunkSize);
            if (viewIn == NULL) {
                CloseHandle(hMapIn);
                CloseHandle(hFileIn);
                CloseHandle(hFileOut);
                return KINETIC_ERR_MAP_FAILED;
            }

            /* XOR setiap byte dalam chunk — kecepatan cache CPU! */
            for (i = 0; i < chunkSize; i++) {
                buffer[i] = viewIn[i] ^ xor_key;
            }

            UnmapViewOfFile(viewIn);

            /* Tulis chunk terenkripsi ke output */
            WriteFile(hFileOut, buffer, chunkSize, &written, NULL);
            offset += chunkSize;
        }

        /* 6. Cleanup */
        CloseHandle(hMapIn);
        CloseHandle(hFileIn);
        CloseHandle(hFileOut);

        return KINETIC_OK;
    }

    int kinetic_byte_invert(const char* input_path, const char* output_path) {
        HANDLE hFileIn, hFileOut;
        LARGE_INTEGER fileSize;
        HANDLE hMapIn;
        unsigned char* viewIn;
        DWORD written;
        unsigned char buffer[KINETIC_BUFFER_SIZE];
        LONGLONG offset;
        DWORD chunkSize;
        size_t i;

        hFileIn = CreateFileA(input_path, GENERIC_READ, FILE_SHARE_READ, NULL,
                              OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFileIn == INVALID_HANDLE_VALUE) return KINETIC_ERR_OPEN_IN;

        GetFileSizeEx(hFileIn, &fileSize);

        hFileOut = CreateFileA(output_path, GENERIC_WRITE, 0, NULL,
                               CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFileOut == INVALID_HANDLE_VALUE) {
            CloseHandle(hFileIn);
            return KINETIC_ERR_OPEN_OUT;
        }

        hMapIn = CreateFileMappingA(hFileIn, NULL, PAGE_READONLY, 0, 0, NULL);
        if (hMapIn == NULL) {
            CloseHandle(hFileIn);
            CloseHandle(hFileOut);
            return KINETIC_ERR_MAP_FAILED;
        }

        offset = 0;
        while (offset < fileSize.QuadPart) {
            chunkSize = KINETIC_BUFFER_SIZE;
            if (offset + chunkSize > (DWORD)fileSize.QuadPart) {
                chunkSize = (DWORD)(fileSize.QuadPart - offset);
            }

            viewIn = (unsigned char*)MapViewOfFile(hMapIn, FILE_MAP_READ,
                         (DWORD)(offset >> 32), (DWORD)(offset & 0xFFFFFFFF), chunkSize);
            if (viewIn == NULL) {
                CloseHandle(hMapIn);
                CloseHandle(hFileIn);
                CloseHandle(hFileOut);
                return KINETIC_ERR_MAP_FAILED;
            }

            /* Inversi setiap byte (~byte) */
            for (i = 0; i < chunkSize; i++) {
                buffer[i] = ~viewIn[i];
            }

            UnmapViewOfFile(viewIn);
            WriteFile(hFileOut, buffer, chunkSize, &written, NULL);
            offset += chunkSize;
        }

        CloseHandle(hMapIn);
        CloseHandle(hFileIn);
        CloseHandle(hFileOut);
        return KINETIC_OK;
    }

    int kinetic_checksum(const char* file_path, unsigned int* out_checksum) {
        HANDLE hFile;
        LARGE_INTEGER fileSize;
        HANDLE hMap;
        unsigned char* view;
        unsigned int checksum;
        LONGLONG offset;
        DWORD chunkSize;
        size_t i;

        hFile = CreateFileA(file_path, GENERIC_READ, FILE_SHARE_READ, NULL,
                            OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hFile == INVALID_HANDLE_VALUE) return KINETIC_ERR_OPEN_IN;

        GetFileSizeEx(hFile, &fileSize);

        hMap = CreateFileMappingA(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
        if (hMap == NULL) {
            CloseHandle(hFile);
            return KINETIC_ERR_MAP_FAILED;
        }

        checksum = 0;
        offset = 0;
        while (offset < fileSize.QuadPart) {
            chunkSize = KINETIC_BUFFER_SIZE;
            if (offset + chunkSize > (DWORD)fileSize.QuadPart) {
                chunkSize = (DWORD)(fileSize.QuadPart - offset);
            }

            view = (unsigned char*)MapViewOfFile(hMap, FILE_MAP_READ,
                       (DWORD)(offset >> 32), (DWORD)(offset & 0xFFFFFFFF), chunkSize);
            if (view == NULL) {
                CloseHandle(hMap);
                CloseHandle(hFile);
                return KINETIC_ERR_MAP_FAILED;
            }

            for (i = 0; i < chunkSize; i++) {
                checksum = checksum ^ ((unsigned int)view[i] << ((i & 3) * 8));
            }

            UnmapViewOfFile(view);
            offset += chunkSize;
        }

        CloseHandle(hMap);
        CloseHandle(hFile);
        *out_checksum = checksum;
        return KINETIC_OK;
    }

#else
    /* LINUX / POSIX IMPLEMENTATION */
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <sys/stat.h>
    #include <unistd.h>

    int kinetic_xor_encrypt(const char* input_path, const char* output_path, unsigned char xor_key) {
        int fd_in, fd_out;
        struct stat sb;
        size_t length;
        char* data_in;
        char* data_out;
        size_t i;

        /* 1. Buka file input */
        fd_in = open(input_path, O_RDONLY);
        if (fd_in < 0) return KINETIC_ERR_OPEN_IN;

        fstat(fd_in, &sb);
        length = sb.st_size;

        /* 2. Buka file output */
        fd_out = open(output_path, O_RDWR | O_CREAT | O_TRUNC, 0644);
        if (fd_out < 0) { close(fd_in); return KINETIC_ERR_OPEN_OUT; }
        ftruncate(fd_out, length);

        /* 3. SIHIR BARE-METAL: mmap */
        data_in = (char*)mmap(NULL, length, PROT_READ, MAP_PRIVATE, fd_in, 0);
        data_out = (char*)mmap(NULL, length, PROT_WRITE, MAP_SHARED, fd_out, 0);

        if (data_in == MAP_FAILED || data_out == MAP_FAILED) {
            close(fd_in);
            close(fd_out);
            return KINETIC_ERR_MAP_FAILED;
        }

        /* 4. KINETIC LOOP: XOR di kecepatan cache CPU */
        for (i = 0; i < length; i++) {
            data_out[i] = data_in[i] ^ xor_key;
        }

        /* 5. Cleanup */
        munmap(data_in, length);
        munmap(data_out, length);
        close(fd_in);
        close(fd_out);

        return KINETIC_OK;
    }

    int kinetic_byte_invert(const char* input_path, const char* output_path) {
        int fd_in, fd_out;
        struct stat sb;
        size_t length;
        char* data_in;
        char* data_out;
        size_t i;

        fd_in = open(input_path, O_RDONLY);
        if (fd_in < 0) return KINETIC_ERR_OPEN_IN;

        fstat(fd_in, &sb);
        length = sb.st_size;

        fd_out = open(output_path, O_RDWR | O_CREAT | O_TRUNC, 0644);
        if (fd_out < 0) { close(fd_in); return KINETIC_ERR_OPEN_OUT; }
        ftruncate(fd_out, length);

        data_in = (char*)mmap(NULL, length, PROT_READ, MAP_PRIVATE, fd_in, 0);
        data_out = (char*)mmap(NULL, length, PROT_WRITE, MAP_SHARED, fd_out, 0);

        if (data_in == MAP_FAILED || data_out == MAP_FAILED) {
            close(fd_in);
            close(fd_out);
            return KINETIC_ERR_MAP_FAILED;
        }

        for (i = 0; i < length; i++) {
            data_out[i] = ~data_in[i];
        }

        munmap(data_in, length);
        munmap(data_out, length);
        close(fd_in);
        close(fd_out);
        return KINETIC_OK;
    }

    int kinetic_checksum(const char* file_path, unsigned int* out_checksum) {
        int fd;
        struct stat sb;
        size_t length;
        unsigned char* data;
        unsigned int checksum;
        size_t i;

        fd = open(file_path, O_RDONLY);
        if (fd < 0) return KINETIC_ERR_OPEN_IN;

        fstat(fd, &sb);
        length = sb.st_size;

        data = (unsigned char*)mmap(NULL, length, PROT_READ, MAP_PRIVATE, fd, 0);
        if (data == MAP_FAILED) {
            close(fd);
            return KINETIC_ERR_MAP_FAILED;
        }

        checksum = 0;
        for (i = 0; i < length; i++) {
            checksum = checksum ^ ((unsigned int)data[i] << ((i & 3) * 8));
        }

        munmap(data, length);
        close(fd);
        *out_checksum = checksum;
        return KINETIC_OK;
    }

#endif /* _WIN32 */

/* ==========================================
 * PLATFORM-INDEPENDENT FUNCTIONS
 * ========================================== */

const char* kinetic_version(void) {
    return "OMNI-KINETIC/2.0.0 (Native C Hyper-Engine)";
}
