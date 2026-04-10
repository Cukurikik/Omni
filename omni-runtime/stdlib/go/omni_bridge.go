package omnistd

// ============================================================
// OMNI Golang Bridge — CGO Zero-Copy Nexus
// ============================================================
// Layer: Network (goroutine, channel, HTTP/2-3)
// Go menggunakan CGO bawaan — TIDAK perlu `go get` eksternal.
// ============================================================

/*
#cgo CFLAGS: -I../../core/target/release
#cgo LDFLAGS: -L../../core/target/release -lomni_core

#include <stdint.h>
#include <stdlib.h>

// OMNI C-ABI Signature (diekspor oleh Rust cdylib)
extern void* __omni_ffi(void* args_buffer, size_t len);
*/
import "C"
import (
	"fmt"
	"unsafe"
)

// OmniResult merepresentasikan monadic Result<T, E> dari Rust
type OmniResult struct {
	Ptr    unsafe.Pointer
	Len    int
	ErrMsg string
}

// Execute memanggil fungsi OMNI melalui batas C-ABI.
// Data dikirim sebagai pointer mentah tanpa serialisasi JSON/Protobuf.
func Execute(functionName string, data []byte) (*OmniResult, error) {
	if len(data) == 0 {
		return nil, fmt.Errorf("[OMNI-E201] data tidak boleh kosong")
	}

	// Kirim pointer langsung — bukan copy!
	cData := C.CBytes(data)
	defer C.free(cData)

	resultPtr := C.__omni_ffi(cData, C.size_t(len(data)))
	if resultPtr == nil {
		return nil, fmt.Errorf("[OMNI-E202] kernel mengembalikan null pointer")
	}

	return &OmniResult{
		Ptr: resultPtr,
		Len: len(data),
	}, nil
}

// SpawnGoroutine mendelegasikan goroutine Go ke OmniEventLoop (Phase 12).
// Ini memungkinkan penjadwalan green thread dari Go ↔ Tokio Rust.
func SpawnGoroutine(taskName string, payload []byte, callback func([]byte)) {
	go func() {
		result, err := Execute(taskName, payload)
		if err != nil {
			fmt.Printf("[OMNI-GOROUTINE] Error: %v\n", err)
			return
		}
		// Convert C pointer back to Go slice
		goBytes := C.GoBytes(result.Ptr, C.int(result.Len))
		callback(goBytes)
	}()
}
