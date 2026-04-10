package omni_web

import "C"

//export OmniGoHandler
func OmniGoHandler() *C.char {
    response := `{"language": "Go", "status": "200 OK", "message": "Goroutines attached to Omni-Threads"}`
    return C.CString(response)
}
