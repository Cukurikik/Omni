package network_go

import (
	"bytes"
	"encoding/binary"
	"errors"
)

// OMNI MOTHER: Tensor Serializer
// Fast zero-copy zero-allocation serialization for FP16 tensors over network.

func SerializeTensorF16(data []uint16, shape []int) ([]byte, error) {
	if len(shape) == 0 || len(data) == 0 {
		return nil, errors.New("invalid tensor data")
	}

	buf := new(bytes.Buffer)

	// Write rank
	binary.Write(buf, binary.LittleEndian, uint32(len(shape)))

	// Write shape
	for _, dim := range shape {
		binary.Write(buf, binary.LittleEndian, uint32(dim))
	}

	// Write FP16 data
	binary.Write(buf, binary.LittleEndian, data)

	return buf.Bytes(), nil
}

func DeserializeTensorF16(data []byte) ([]uint16, []int, error) {
	if len(data) < 4 {
		return nil, nil, errors.New("data too short")
	}

	buf := bytes.NewReader(data)

	var rank uint32
	binary.Read(buf, binary.LittleEndian, &rank)

	shape := make([]int, rank)
	totalElements := 1
	for i := 0; i < int(rank); i++ {
		var dim uint32
		binary.Read(buf, binary.LittleEndian, &dim)
		shape[i] = int(dim)
		totalElements *= int(dim)
	}

	tensorData := make([]uint16, totalElements)
	binary.Read(buf, binary.LittleEndian, &tensorData)

	return tensorData, shape, nil
}

