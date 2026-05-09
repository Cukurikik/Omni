/*
 * omni_mmap_weights.c — Zero-Copy Model Loader via mmap
 * Layer: System / Memory
 * Inspired by: ggerganov/llama.cpp
 *
 * Maps a large AI model file (like .gguf or .safetensors) directly into
 * the virtual address space using the POSIX mmap syscall. This avoids reading
 * gigantic weight files into RAM twice and allows OS-level demand paging.
 * Zero mock.
 */

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <errno.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

typedef struct {
    void* addr;
    size_t size;
    int fd;
} OmniMappedModel;

/**
 * Memory maps a file into RAM as read-only.
 */
OmniMappedModel* omni_mmap_model(const char* filepath) {
    OmniMappedModel* map = (OmniMappedModel*)malloc(sizeof(OmniMappedModel));
    if (!map) return NULL;

#ifdef _WIN32
    HANDLE hFile = CreateFileA(filepath, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        free(map);
        return NULL;
    }

    LARGE_INTEGER fileSize;
    GetFileSizeEx(hFile, &fileSize);
    map->size = fileSize.QuadPart;

    HANDLE hMapping = CreateFileMappingA(hFile, NULL, PAGE_READONLY, 0, 0, NULL);
    if (hMapping == NULL) {
        CloseHandle(hFile);
        free(map);
        return NULL;
    }

    map->addr = MapViewOfFile(hMapping, FILE_MAP_READ, 0, 0, 0);
    
    // Windows requires keeping handles to unmap, but for simple structural mapping
    // saving addr and size is enough for this implementation.
    // In production, handles should be stored in the struct.
    CloseHandle(hMapping);
    CloseHandle(hFile);

    if (map->addr == NULL) {
        free(map);
        return NULL;
    }

    map->fd = -1; // Unused in Windows for unmap
#else
    map->fd = open(filepath, O_RDONLY);
    if (map->fd == -1) {
        free(map);
        return NULL;
    }

    struct stat sb;
    if (fstat(map->fd, &sb) == -1) {
        close(map->fd);
        free(map);
        return NULL;
    }
    map->size = sb.st_size;

    map->addr = mmap(NULL, map->size, PROT_READ, MAP_SHARED, map->fd, 0);
    if (map->addr == MAP_FAILED) {
        close(map->fd);
        free(map);
        return NULL;
    }
#endif

    return map;
}

/**
 * Unmaps the file and frees resources.
 */
void omni_munmap_model(OmniMappedModel* map) {
    if (!map) return;

#ifdef _WIN32
    if (map->addr) {
        UnmapViewOfFile(map->addr);
    }
#else
    if (map->addr && map->addr != MAP_FAILED) {
        munmap(map->addr, map->size);
    }
    if (map->fd != -1) {
        close(map->fd);
    }
#endif

    free(map);
}
