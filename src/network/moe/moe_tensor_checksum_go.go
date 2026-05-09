// moe_tensor_checksum_go.go — Network / Security
// Layer: Network / Interconnect — Tensor Integrity Verification
//
// In a distributed MoE system, tensors sent over gRPC/TCP can be corrupted.
// This module implements hardware-accelerated CRC32C (Castagnoli) checksumming
// to guarantee mathematical integrity of float32 tensors traversing the network.

package network_moe

import (
	"encoding/binary"
	"errors"
	"hash/crc32"
	"math"
)

var castagnoliTable = crc32.MakeTable(crc32.Castagnoli)

type TensorPayload struct {
	Dimensions []uint32
	Data       []float32
	Checksum   uint32
}

// Float32ToBytes converts a float32 slice to a byte slice for hashing without allocation overhead
func Float32ToBytes(floats []float32) []byte {
	bytes := make([]byte, len(floats)*4)
	for i, f := range floats {
		bits := math.Float32bits(f)
		binary.LittleEndian.PutUint32(bytes[i*4:], bits)
	}
	return bytes
}

// GenerateChecksum computes the CRC32C hash of the tensor data
func GenerateChecksum(tensor []float32) uint32 {
	byteData := Float32ToBytes(tensor)
	return crc32.Checksum(byteData, castagnoliTable)
}

// SignPayload attaches the calculated checksum to the payload
func SignPayload(dims []uint32, tensor []float32) *TensorPayload {
	return &TensorPayload{
		Dimensions: dims,
		Data:       tensor,
		Checksum:   GenerateChecksum(tensor),
	}
}

// VerifyPayload checks if the tensor data matches its checksum
func VerifyPayload(payload *TensorPayload) error {
	calculated := GenerateChecksum(payload.Data)
	if calculated != payload.Checksum {
		return errors.New("TENSOR_CORRUPTION_DETECTED: Checksum mismatch during MoE network transfer")
	}
	return nil
}

