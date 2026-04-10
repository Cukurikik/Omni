// ==========================================
// 🐍 OMNI-VENOM: NATIVE PYTHON BRIDGE (CGO)
// ==========================================
// File ini aktif HANYA jika CGO_ENABLED=1 DAN python3 ditemukan.
// Menginjeksi CPython Interpreter langsung ke dalam memori Golang!
//
// Developer TypeScript bisa mengeksekusi kode Python tanpa:
//   ❌ Flask / FastAPI server terpisah
//   ❌ HTTP overhead
//   ❌ JSON serialization/deserialization melalui jaringan
//
// Alur: TypeScript → V8 → Syscall → Golang → CPython (in-process!)
//
// Build requirement:
//   - Python 3.10+ dengan header dev (python3-dev / python3-devel)
//   - pkg-config python3 harus bisa ditemukan
//   - CGO_ENABLED=1
// ==========================================

//go:build cgo && python

package net

/*
// Windows: Manual Python 3.12 path (no pkg-config needed)
#cgo windows CFLAGS: -IC:/Users/IKYY/AppData/Local/Programs/Python/Python312/Include
#cgo windows LDFLAGS: -LC:/Users/IKYY/AppData/Local/Programs/Python/Python312/libs -lpython312

// Linux/Mac: Use pkg-config as standard
#cgo linux pkg-config: python3-embed
#cgo darwin pkg-config: python3-embed

#include <Python.h>
*/
import "C"
import (
	"encoding/json"
	"fmt"
	"log"
	"sync"
	"unsafe"
)

// ==========================================
// 🐍 VENOM ENGINE: SINGLETON PYTHON RUNTIME
// ==========================================

type VenomEngine struct {
	mu          sync.Mutex
	initialized bool
	scriptsDir  string
}

var (
	venomInstance *VenomEngine
	venomOnce    sync.Once
)

// GetVenom returns the singleton VenomEngine
func GetVenom() *VenomEngine {
	venomOnce.Do(func() {
		venomInstance = &VenomEngine{
			scriptsDir: "./venom_scripts",
		}
	})
	return venomInstance
}

// IgnitePythonMatrix initializes CPython interpreter
func (v *VenomEngine) IgnitePythonMatrix() error {
	v.mu.Lock()
	defer v.mu.Unlock()

	if v.initialized {
		log.Println("🐍 [OMNI-VENOM] Python sudah aktif — skip re-init")
		return nil
	}

	log.Println("🐍 [OMNI-VENOM] Menyalakan Reaktor CPython di dalam Golang...")

	// Initialize CPython interpreter
	C.Py_Initialize()

	if C.Py_IsInitialized() == 0 {
		return fmt.Errorf("OMNI-VENOM: Gagal menginisialisasi CPython")
	}

	// Add venom_scripts directory to Python's sys.path
	addPathCode := C.CString(fmt.Sprintf(`
import sys
import os
scripts_dir = os.path.abspath('%s')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
print(f"🐍 [VENOM] sys.path updated: {scripts_dir}")
`, v.scriptsDir))
	defer C.free(unsafe.Pointer(addPathCode))

	C.PyRun_SimpleString(addPathCode)

	v.initialized = true
	log.Println("🐍 [OMNI-VENOM] CPython Reactor ONLINE! Python scripts: ", v.scriptsDir)

	return nil
}

// ExecutePythonScript runs a Python function and returns JSON result
func (v *VenomEngine) ExecutePythonScript(scriptName, functionName, jsonArgs string) (string, error) {
	v.mu.Lock()
	defer v.mu.Unlock()

	if !v.initialized {
		return "", fmt.Errorf("OMNI-VENOM: CPython belum diinisialisasi. Panggil IgnitePythonMatrix() dulu")
	}

	// Import the module
	cModuleName := C.CString(scriptName)
	defer C.free(unsafe.Pointer(cModuleName))

	pModule := C.PyImport_ImportModule(cModuleName)
	if pModule == nil {
		C.PyErr_Print()
		return "", fmt.Errorf("OMNI-VENOM: Gagal import modul Python '%s'", scriptName)
	}
	defer C.Py_DecRef(pModule)

	// Get the function
	cFuncName := C.CString(functionName)
	defer C.free(unsafe.Pointer(cFuncName))

	pFunc := C.PyObject_GetAttrString(pModule, cFuncName)
	if pFunc == nil || C.PyCallable_Check(pFunc) == 0 {
		if pFunc != nil {
			C.Py_DecRef(pFunc)
		}
		C.PyErr_Print()
		return "", fmt.Errorf("OMNI-VENOM: Fungsi '%s' tidak ditemukan di '%s'", functionName, scriptName)
	}
	defer C.Py_DecRef(pFunc)

	// Parse JSON args and pass as Python dict
	cJsonArgs := C.CString(jsonArgs)
	defer C.free(unsafe.Pointer(cJsonArgs))

	// Use json module to parse args in Python
	parseScript := fmt.Sprintf(`
import json
__venom_args = json.loads('%s')
`, escapeForPython(jsonArgs))
	cParseScript := C.CString(parseScript)
	defer C.free(unsafe.Pointer(cParseScript))
	C.PyRun_SimpleString(cParseScript)

	// Get the parsed args from __main__
	mainModule := C.PyImport_AddModule(C.CString("__main__"))
	mainDict := C.PyModule_GetDict(mainModule)
	pArgs := C.PyDict_GetItemString(mainDict, C.CString("__venom_args"))

	// Call the function with the args
	var pResult *C.PyObject
	if pArgs != nil {
		pTuple := C.PyTuple_New(1)
		C.Py_IncRef(pArgs)
		C.PyTuple_SetItem(pTuple, 0, pArgs)
		pResult = C.PyObject_CallObject(pFunc, pTuple)
		C.Py_DecRef(pTuple)
	} else {
		pResult = C.PyObject_CallObject(pFunc, nil)
	}

	if pResult == nil {
		C.PyErr_Print()
		return "", fmt.Errorf("OMNI-VENOM: Eksekusi '%s.%s()' gagal", scriptName, functionName)
	}
	defer C.Py_DecRef(pResult)

	// Convert result to string
	pStr := C.PyObject_Str(pResult)
	if pStr == nil {
		return "", fmt.Errorf("OMNI-VENOM: Gagal mengonversi hasil Python ke string")
	}
	defer C.Py_DecRef(pStr)

	cStr := C.PyUnicode_AsUTF8(pStr)
	goResult := C.GoString(cStr)

	return goResult, nil
}

// ExecuteRawPython runs raw Python code string
func (v *VenomEngine) ExecuteRawPython(code string) (string, error) {
	v.mu.Lock()
	defer v.mu.Unlock()

	if !v.initialized {
		return "", fmt.Errorf("OMNI-VENOM: CPython belum diinisialisasi")
	}

	// Wrap code to capture output
	wrappedCode := fmt.Sprintf(`
import io, sys
__venom_capture = io.StringIO()
sys.stdout = __venom_capture
try:
%s
except Exception as e:
    print(f"ERROR: {e}")
finally:
    sys.stdout = sys.__stdout__
__venom_output = __venom_capture.getvalue()
`, indentPythonCode(code, "    "))

	cCode := C.CString(wrappedCode)
	defer C.free(unsafe.Pointer(cCode))

	C.PyRun_SimpleString(cCode)

	// Get captured output
	mainModule := C.PyImport_AddModule(C.CString("__main__"))
	mainDict := C.PyModule_GetDict(mainModule)
	pOutput := C.PyDict_GetItemString(mainDict, C.CString("__venom_output"))

	if pOutput == nil {
		return "", nil
	}

	cOutput := C.PyUnicode_AsUTF8(pOutput)
	return C.GoString(cOutput), nil
}

// GetVenomStatus returns current Python engine status
func (v *VenomEngine) GetVenomStatus() map[string]interface{} {
	v.mu.Lock()
	defer v.mu.Unlock()

	pyVersion := "NOT_INITIALIZED"
	if v.initialized {
		cVersion := C.Py_GetVersion()
		pyVersion = C.GoString(cVersion)
	}

	return map[string]interface{}{
		"initialized": v.initialized,
		"python_version": pyVersion,
		"scripts_dir":   v.scriptsDir,
		"mode":          "NATIVE_CPYTHON",
		"bridge":        "CGO_DIRECT",
	}
}

// ShutdownPython finalizes CPython
func (v *VenomEngine) ShutdownPython() {
	v.mu.Lock()
	defer v.mu.Unlock()

	if v.initialized {
		log.Println("🐍 [OMNI-VENOM] Shutting down CPython Reactor...")
		C.Py_Finalize()
		v.initialized = false
	}
}

// Helper: escape JSON string for Python
func escapeForPython(s string) string {
	// Simple escape for single quotes in Python string
	result := ""
	for _, c := range s {
		switch c {
		case '\'':
			result += "\\'"
		case '\\':
			result += "\\\\"
		case '\n':
			result += "\\n"
		case '\r':
			result += "\\r"
		default:
			result += string(c)
		}
	}
	return result
}

// Helper: indent Python code
func indentPythonCode(code, prefix string) string {
	result := ""
	for i, line := range venomSplitLines(code) {
		if i > 0 {
			result += "\n"
		}
		if line != "" {
			result += prefix + line
		}
	}
	return result
}

func venomSplitLines(s string) []string {
	var lines []string
	current := ""
	for _, c := range s {
		if c == '\n' {
			lines = append(lines, current)
			current = ""
		} else {
			current += string(c)
		}
	}
	if current != "" {
		lines = append(lines, current)
	}
	return lines
}

// VenomHandleSyscall processes venom_* syscalls from TypeScript → V8 → Rust → Go
func VenomHandleSyscall(command string, argsJSON string) string {
	venom := GetVenom()
	var args map[string]interface{}
	json.Unmarshal([]byte(argsJSON), &args)

	switch command {
	case "venom_execute":
		script, _ := args["script"].(string)
		funcName, _ := args["func"].(string)
		payload, _ := args["payload"].(string)

		result, err := venom.ExecutePythonScript(script, funcName, payload)
		if err != nil {
			errJSON, _ := json.Marshal(map[string]string{"error": err.Error()})
			return string(errJSON)
		}
		resultJSON, _ := json.Marshal(map[string]string{"result": result})
		return string(resultJSON)

	case "venom_raw":
		code, _ := args["code"].(string)
		output, err := venom.ExecuteRawPython(code)
		if err != nil {
			errJSON, _ := json.Marshal(map[string]string{"error": err.Error()})
			return string(errJSON)
		}
		resultJSON, _ := json.Marshal(map[string]string{"output": output})
		return string(resultJSON)

	case "venom_status":
		status := venom.GetVenomStatus()
		statusJSON, _ := json.Marshal(status)
		return string(statusJSON)

	case "venom_ignite":
		if dir, ok := args["scripts_dir"].(string); ok {
			venom.scriptsDir = dir
		}
		err := venom.IgnitePythonMatrix()
		if err != nil {
			errJSON, _ := json.Marshal(map[string]string{"error": err.Error()})
			return string(errJSON)
		}
		resultJSON, _ := json.Marshal(map[string]string{"status": "PYTHON_ONLINE"})
		return string(resultJSON)

	default:
		errJSON, _ := json.Marshal(map[string]string{"error": fmt.Sprintf("Venom command tidak dikenal: %s", command)})
		return string(errJSON)
	}
}
