import Foundation

// ============================================================
// OMNI Swift Bridge — Spatial/Mobile Nexus
// ============================================================
// Layer: UI/Mobile (Apple Ecosystem, Spatial Computing)
// Swift menggunakan C-Interop bawaan — TIDAK perlu SPM package.
// Butuh Bridging-Header.h yang men-include omni_std.h
// ============================================================

/// Monadic Result dari kernel OMNI
public enum OmniResult<T> {
    case ok(T)
    case err(code: String, message: String)
}

/// Jembatan utama Swift ↔ OMNI Kernel
public final class OmniBridge {

    public static let shared = OmniBridge()

    private init() {}

    /// Eksekusi fungsi OMNI melalui C-ABI.
    /// Data ditransmisikan via UnsafeRawPointer tanpa bridging overhead.
    public func execute(functionName: String, data: Data) -> OmniResult<UnsafeRawPointer> {
        return data.withUnsafeBytes { rawBuffer -> OmniResult<UnsafeRawPointer> in
            guard let baseAddress = rawBuffer.baseAddress else {
                return .err(code: "E801", message: "Data buffer kosong")
            }

            // __omni_ffi diekspor via Bridging-Header.h → omni_std.h
            let resultPtr = __omni_ffi(
                UnsafeMutableRawPointer(mutating: baseAddress),
                data.count
            )

            guard let validPtr = resultPtr else {
                return .err(code: "E802", message: "Kernel mengembalikan null")
            }

            return .ok(UnsafeRawPointer(validPtr))
        }
    }

    /// Zero-copy dispatch untuk array numerik (Metal/GPU compute)
    public func executeSIMD(_ floats: [Float]) -> OmniResult<UnsafeRawPointer> {
        let data = floats.withUnsafeBytes { Data($0) }
        return execute(functionName: "swift_simd_dispatch", data: data)
    }
}
