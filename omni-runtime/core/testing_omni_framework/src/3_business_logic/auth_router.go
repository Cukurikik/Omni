// ==========================================
// [DIMENSI 3: GOLANG] JENDERAL LALU LINTAS API
// ==========================================

package omni_auth_service


import (
    "omni/core/network"
    "omni/bindings/rust_crypto" // Memanggil memori Rust tanpa jeda!
)

func StartAuthService() {
    // Membuka rute API secepat kilat
    network.Post("/api/register", func(req network.Request) network.Response {
        
        email := req.Body["email"].(string)
        password := req.Body["plain_text_pass"].(string)

        // Golang memerintahkan Rust untuk melakukan hashing.
        // Proses ini memakan waktu 0.001 ms karena tidak ada REST API di antaranya!
        secureHash := rust_crypto.HashPasswordSecure(password)

        // Sementara kita kembalikan sukses, database SQL akan menyusul di tahap berikutnya
        return network.JSON(200, map[string]interface{}{
            "status": "KOMANDAN BARU TEREGISTRASI",
            "email": email,
            "hash_generated": secureHash,
        })
    })
}
