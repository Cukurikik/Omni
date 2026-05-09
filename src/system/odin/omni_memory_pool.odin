// OMNI System Layer — Odin High-Performance Memory Pool
// Zero-fragmentation arena allocator for inference workloads.

package omni_memory

import "core:fmt"
import "core:mem"
import "core:sync"

ARENA_DEFAULT_SIZE :: 64 * 1024 * 1024 // 64MB default

Arena :: struct {
    buffer:     []byte,
    offset:     int,
    capacity:   int,
    peak_usage: int,
    alloc_count: int,
    mutex:      sync.Mutex,
}

arena_create :: proc(size: int = ARENA_DEFAULT_SIZE) -> ^Arena {
    arena := new(Arena)
    arena.buffer = make([]byte, size)
    arena.capacity = size
    arena.offset = 0
    arena.peak_usage = 0
    arena.alloc_count = 0
    return arena
}

arena_alloc :: proc(arena: ^Arena, size: int, alignment: int = 16) -> rawptr {
    sync.mutex_lock(&arena.mutex)
    defer sync.mutex_unlock(&arena.mutex)

    // Align offset
    aligned := (arena.offset + alignment - 1) & ~(alignment - 1)
    if aligned + size > arena.capacity {
        fmt.eprintfln("Arena OOM: requested %d, available %d", size, arena.capacity - aligned)
        return nil
    }

    ptr := &arena.buffer[aligned]
    arena.offset = aligned + size
    arena.alloc_count += 1

    if arena.offset > arena.peak_usage {
        arena.peak_usage = arena.offset
    }

    return rawptr(ptr)
}

arena_alloc_typed :: proc(arena: ^Arena, $T: typeid, count: int = 1) -> [^]T {
    size := size_of(T) * count
    ptr := arena_alloc(arena, size, align_of(T))
    if ptr == nil { return nil }
    return ([^]T)(ptr)
}

arena_reset :: proc(arena: ^Arena) {
    sync.mutex_lock(&arena.mutex)
    defer sync.mutex_unlock(&arena.mutex)
    mem.zero_slice(arena.buffer[:arena.offset])
    arena.offset = 0
    arena.alloc_count = 0
}

arena_destroy :: proc(arena: ^Arena) {
    delete(arena.buffer)
    free(arena)
}

arena_usage :: proc(arena: ^Arena) -> (used: int, total: int, peak: int) {
    return arena.offset, arena.capacity, arena.peak_usage
}

arena_utilization :: proc(arena: ^Arena) -> f64 {
    if arena.capacity == 0 { return 0.0 }
    return f64(arena.offset) / f64(arena.capacity) * 100.0
}

// Pool allocator for fixed-size inference buffers
BufferPool :: struct {
    arena:      ^Arena,
    buffer_size: int,
    free_list:  [dynamic]rawptr,
    total:      int,
    in_use:     int,
}

pool_create :: proc(buffer_size: int, initial_count: int) -> ^BufferPool {
    pool := new(BufferPool)
    pool.arena = arena_create(buffer_size * initial_count * 2)
    pool.buffer_size = buffer_size
    pool.total = initial_count
    pool.in_use = 0

    for i in 0..<initial_count {
        buf := arena_alloc(pool.arena, buffer_size)
        if buf != nil {
            append(&pool.free_list, buf)
        }
    }

    return pool
}

pool_acquire :: proc(pool: ^BufferPool) -> rawptr {
    if len(pool.free_list) > 0 {
        buf := pop(&pool.free_list)
        pool.in_use += 1
        return buf
    }
    // Grow
    buf := arena_alloc(pool.arena, pool.buffer_size)
    if buf != nil {
        pool.total += 1
        pool.in_use += 1
    }
    return buf
}

pool_release :: proc(pool: ^BufferPool, buf: rawptr) {
    mem.zero(buf, pool.buffer_size)
    append(&pool.free_list, buf)
    pool.in_use -= 1
}

pool_destroy :: proc(pool: ^BufferPool) {
    delete(pool.free_list)
    arena_destroy(pool.arena)
    free(pool)
}
