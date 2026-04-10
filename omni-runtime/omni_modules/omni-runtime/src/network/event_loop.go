// ============================================================
// 🌐 omni-runtime/network/event_loop.go — OMNI Event Loop & Goroutines
// ============================================================

package runtime

import (
    "errors"
    "sync"
    "sync/atomic"
    "time"
)

// Monadic Result wrapper for Go -> OMNI bridge
type OMNIResult[T any] struct {
    Ok    T
    Error error
}

type TaskId uint64

var (
    globalTaskCounter uint64 = 0
    activeTasks       sync.Map
)

// spawn memicu green thread di Golang, dipanggil oleh OMNI compiler
// menggunakan `go spawn` translation
//export omni_spawn_goroutine
func OmniSpawnGoroutine(taskFn func()) OMNIResult[TaskId] {
    if taskFn == nil {
        return OMNIResult[TaskId]{Error: errors.New("E201: Task function cannot be nil")}
    }

    id := TaskId(atomic.AddUint64(&globalTaskCounter, 1))
    
    // Simpan task state (seolah-olah Promise pending)
    activeTasks.Store(id, true)

    go func() {
        defer func() {
            // Panic recovery untuk menjaga stabilitas runtime
            if r := recover(); r != nil {
                // Log runtime error (akan diteruskan ke omni-log di atas)
            }
            activeTasks.Delete(id)
        }()
        
        taskFn()
    }()

    return OMNIResult[TaskId]{Ok: id}
}

//export omni_set_timeout
func OmniSetTimeout(taskFn func(), ms uint32) OMNIResult[TaskId] {
    if taskFn == nil {
        return OMNIResult[TaskId]{Error: errors.New("E202: Timer task cannot be nil")}
    }

    id := TaskId(atomic.AddUint64(&globalTaskCounter, 1))
    activeTasks.Store(id, true)

    time.AfterFunc(time.Duration(ms)*time.Millisecond, func() {
        defer activeTasks.Delete(id)
        taskFn()
    })

    return OMNIResult[TaskId]{Ok: id}
}
