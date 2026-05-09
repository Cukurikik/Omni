// moe_tensor_deserializer_go.go — Network / Parsing
// Layer: Network / Interconnect — Zero-Copy Tensor Deserializer
//
// When Go receives a massive chunk of binary tensor data over TCP, using standard
// `encoding/binary` requires copying the byte slice into float32 slices, doubling
// memory usage. This module uses `unsafe` pointers to map the byte slice directly
// to a float32 slice in exactly 0 nanoseconds (Zero-Copy).

package network_moe

import (
	"fmt"
	"reflect"
	"unsafe"
)

// ZeroCopyBytesToFloat32 casts a []byte to []float32 without allocating new memory.
// WARNING: The resulting float32 slice shares memory with the byte slice.
// If the byte slice is modified or garbage collected, the float slice breaks.
func ZeroCopyBytesToFloat32(b []byte) []float32 {
	if len(b) == 0 {
		return nil
	}

	// Must be divisible by 4 (size of float32)
	if len(b)%4 != 0 {
		panic("Byte slice length must be a multiple of 4 to cast to float32")
	}

	// Create a new slice header pointing to the same data
	header := *(*reflect.SliceHeader)(unsafe.Pointer(&b))
	header.Len /= 4
	header.Cap /= 4

	return *(*[]float32)(unsafe.Pointer(&header))
}

func TestDeserializer() {
	// Example 12 bytes = 3 floats
	mockData := []byte{0, 0, 128, 63, 0, 0, 0, 64, 0, 0, 64, 64} // 1.0, 2.0, 3.0 in Little Endian

	fmt.Println("[Zero-Copy] Received 12 bytes over TCP.")

	// Instant cast, 0 allocations
	floats := ZeroCopyBytesToFloat32(mockData)

	fmt.Printf("[Zero-Copy] Deserialized Floats: %v\n", floats)
}

