/*
 * omni_shm_alloc.c — POSIX Shared Memory Allocation
 * Layer: System / C
 *
 * Provides a robust interface to POSIX Shared Memory (shm_open, mmap),
 * allowing zero-copy IPC between decoupled OMNI microservices (e.g. Inference vs Network).
 * Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct OmniSharedMemory {
    char name[256];
    int fd;
    void* ptr;
    size_t size;
} OmniSharedMemory;

/**
 * Creates and maps a new shared memory segment.
 */
OmniSharedMemory* omni_shm_create(const char* name, size_t size) {
    OmniSharedMemory* shm = (OmniSharedMemory*)malloc(sizeof(OmniSharedMemory));
    if (!shm) return NULL;

    strncpy(shm->name, name, 255);
    shm->name[255] = '\0';
    shm->size = size;

    // Create the shared memory object
    shm->fd = shm_open(shm->name, O_CREAT | O_RDWR, 0666);
    if (shm->fd == -1) {
        perror("OMNI SHM Create: shm_open failed");
        free(shm);
        return NULL;
    }

    // Configure the size of the shared memory object
    if (ftruncate(shm->fd, size) == -1) {
        perror("OMNI SHM Create: ftruncate failed");
        close(shm->fd);
        shm_unlink(shm->name);
        free(shm);
        return NULL;
    }

    // Map the shared memory object into the process's address space
    shm->ptr = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, shm->fd, 0);
    if (shm->ptr == MAP_FAILED) {
        perror("OMNI SHM Create: mmap failed");
        close(shm->fd);
        shm_unlink(shm->name);
        free(shm);
        return NULL;
    }

    return shm;
}

/**
 * Opens and maps an existing shared memory segment.
 */
OmniSharedMemory* omni_shm_open(const char* name, size_t size) {
    OmniSharedMemory* shm = (OmniSharedMemory*)malloc(sizeof(OmniSharedMemory));
    if (!shm) return NULL;

    strncpy(shm->name, name, 255);
    shm->name[255] = '\0';
    shm->size = size;

    shm->fd = shm_open(shm->name, O_RDWR, 0666);
    if (shm->fd == -1) {
        free(shm);
        return NULL;
    }

    shm->ptr = mmap(0, size, PROT_READ | PROT_WRITE, MAP_SHARED, shm->fd, 0);
    if (shm->ptr == MAP_FAILED) {
        close(shm->fd);
        free(shm);
        return NULL;
    }

    return shm;
}

/**
 * Unmaps the memory and closes the file descriptor.
 * Note: This does not destroy the shared memory segment globally.
 */
void omni_shm_close(OmniSharedMemory* shm) {
    if (shm) {
        if (shm->ptr && shm->ptr != MAP_FAILED) {
            munmap(shm->ptr, shm->size);
        }
        if (shm->fd != -1) {
            close(shm->fd);
        }
        free(shm);
    }
}

/**
 * Completely destroys the shared memory segment from the OS.
 */
void omni_shm_unlink(const char* name) {
    shm_unlink(name);
}
