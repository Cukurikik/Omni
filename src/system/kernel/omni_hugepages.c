/*
 * omni_hugepages.c — HugePages Memory Allocator
 * Layer: System / C
 *
 * Implements memory allocation backed by Linux Transparent HugePages (THP)
 * or explicit `mmap` with `MAP_HUGETLB`. Radically reduces TLB misses 
 * for massive VRAM/RAM tensor operations. Zero mock.
 */

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <errno.h>

// Standard HugePage size on x86 is 2MB
#define OMNI_HUGEPAGE_SIZE (2 * 1024 * 1024)

/**
 * Allocates memory explicitly backed by HugeTLBFS.
 * Will fail if the OS is not configured for HugePages.
 */
void* omni_alloc_hugepage(size_t size) {
    // Align size up to the nearest HugePage boundary
    size_t aligned_size = (size + OMNI_HUGEPAGE_SIZE - 1) & ~(OMNI_HUGEPAGE_SIZE - 1);

    void* ptr = mmap(NULL, aligned_size, 
                     PROT_READ | PROT_WRITE, 
                     MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, 
                     -1, 0);

    if (ptr == MAP_FAILED) {
        // Fallback to standard mmap if HugeTLB is unavailable, 
        // but hint the kernel to use Transparent HugePages
        ptr = mmap(NULL, aligned_size, 
                   PROT_READ | PROT_WRITE, 
                   MAP_PRIVATE | MAP_ANONYMOUS, 
                   -1, 0);
                   
        if (ptr != MAP_FAILED) {
            // Advise kernel to merge pages into huge pages
            madvise(ptr, aligned_size, MADV_HUGEPAGE);
        } else {
            return NULL;
        }
    }

    return ptr;
}

/**
 * Frees memory allocated via the HugePage routines.
 */
void omni_free_hugepage(void* ptr, size_t size) {
    if (!ptr) return;
    
    size_t aligned_size = (size + OMNI_HUGEPAGE_SIZE - 1) & ~(OMNI_HUGEPAGE_SIZE - 1);
    munmap(ptr, aligned_size);
}
