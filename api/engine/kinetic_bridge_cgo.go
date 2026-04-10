//go:build cgo
// +build cgo

package engine

/*
#cgo CFLAGS: -I.
#include "kinetic_engine.h"
#include <stdlib.h>
*/
import "C"
import (
	"fmt"
	"unsafe"
)

func KineticVersion() string {
	val := C.kinetic_version()
	return C.GoString(val)
}

func KineticXorEncrypt(inputPath, outputPath string, xorKey byte) error {
	cIn := C.CString(inputPath)
	cOut := C.CString(outputPath)
	defer C.free(unsafe.Pointer(cIn))
	defer C.free(unsafe.Pointer(cOut))

	res := C.kinetic_xor_encrypt(cIn, cOut, C.uchar(xorKey))
	if res != 0 {
		return fmt.Errorf("kinetic_xor_encrypt failed with error code: %d", int(res))
	}
	return nil
}

func KineticByteInvert(inputPath, outputPath string) error {
	cIn := C.CString(inputPath)
	cOut := C.CString(outputPath)
	defer C.free(unsafe.Pointer(cIn))
	defer C.free(unsafe.Pointer(cOut))

	res := C.kinetic_byte_invert(cIn, cOut)
	if res != 0 {
		return fmt.Errorf("kinetic_byte_invert failed with error code: %d", int(res))
	}
	return nil
}

func KineticChecksum(filePath string) (uint32, error) {
	cPath := C.CString(filePath)
	defer C.free(unsafe.Pointer(cPath))

	var checksum C.uint
	res := C.kinetic_checksum(cPath, &checksum)
	if res != 0 {
		return 0, fmt.Errorf("kinetic_checksum failed with error code: %d", int(res))
	}
	return uint32(checksum), nil
}
