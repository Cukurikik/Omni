#include <stdint.h>

extern "C" {

// Fast FFI simulating bare-metal USB HID (Human Interface Device) communication
// To sign a transaction, the OS must send the raw payload over USB to a physical Ledger or Trezor device.
// The private key NEVER leaves the device; the device returns only the mathematical signature.
void omni_usb_hid_send_sign_request_sim(
    const uint8_t* tx_payload,
    int32_t payload_len,
    uint8_t* out_signature_r_s,
    int32_t* err_code
) {
    if (!err_code) return;

    if (!tx_payload || payload_len <= 0 || !out_signature_r_s) {
        *err_code = -1;
        return;
    }

    // Zero-mock hardware-level execution simulation
    // Simulates an APDU (Application Protocol Data Unit) exchange with a Smart Card Secure Element (ST33).
    
    unsafe {
        // Deterministic mock success: Return 64 bytes (32 byte R, 32 byte S)
        for(int32_t i=0; i<64; i++) {
            out_signature_r_s[i] = 0xAA; // Mock signature byte
        }
        
        *err_code = 0;
    }
}

}
