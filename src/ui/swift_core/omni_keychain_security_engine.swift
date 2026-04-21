// ===========================================================================
// OMNI KEYCHAIN SECURITY ENGINE (SEMESTER 3 — BATCH 38.2)
// ===========================================================================
// Absorbed From  : Apple Keychain Services + CryptoKit + Security framework
// Logic Inherited: Swift / UI Layer (Apple Secure Storage + Crypto)
// ===========================================================================

import Foundation

// MARK: - Error Types (Monadic — no try/catch)

enum KeychainError: Error, CustomStringConvertible {
    case itemNotFound
    case duplicateItem
    case encodingError(String)
    case decodingError(String)
    case accessDenied
    case invalidKey(String)
    case encryptionFailed(String)
    case hashMismatch
    case unknown(Int32)
    
    var description: String {
        switch self {
        case .itemNotFound: return "KeychainError: Item not found"
        case .duplicateItem: return "KeychainError: Duplicate item"
        case .encodingError(let msg): return "KeychainError: Encoding failed - \(msg)"
        case .decodingError(let msg): return "KeychainError: Decoding failed - \(msg)"
        case .accessDenied: return "KeychainError: Access denied"
        case .invalidKey(let key): return "KeychainError: Invalid key - \(key)"
        case .encryptionFailed(let msg): return "KeychainError: Encryption failed - \(msg)"
        case .hashMismatch: return "KeychainError: Hash integrity check failed"
        case .unknown(let code): return "KeychainError: Unknown error (code: \(code))"
        }
    }
}

// MARK: - Result Type Alias

typealias KeychainResult<T> = Result<T, KeychainError>

// MARK: - Keychain Item

struct KeychainItem {
    let key: String
    let data: Data
    let createdAt: Date
    let updatedAt: Date
    let accessLevel: AccessLevel
    let integrityHash: String
    
    enum AccessLevel: String {
        case whenUnlocked = "whenUnlocked"
        case afterFirstUnlock = "afterFirstUnlock"
        case always = "always"
        case whenUnlockedThisDeviceOnly = "whenUnlockedThisDeviceOnly"
    }
}

// MARK: - Crypto Utilities

struct OmniCryptoUtils {
    
    /// SHA-256 hash (manual implementation — no CryptoKit dependency).
    /// Implements the FIPS 180-4 compression function.
    static func sha256(_ data: Data) -> String {
        let bytes = [UInt8](data)
        var h: [UInt32] = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]
        
        let k: [UInt32] = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
            0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
            0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
            0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
            0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
            0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
            0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        ]
        
        // Pre-processing: padding
        var message = bytes
        let originalLength = bytes.count
        message.append(0x80)
        while message.count % 64 != 56 {
            message.append(0x00)
        }
        let bitLength = UInt64(originalLength * 8)
        for i in stride(from: 56, through: 0, by: -8) {
            message.append(UInt8((bitLength >> i) & 0xFF))
        }
        
        // Process each 512-bit (64-byte) block
        for blockStart in stride(from: 0, to: message.count, by: 64) {
            var w = [UInt32](repeating: 0, count: 64)
            
            for i in 0..<16 {
                let offset = blockStart + i * 4
                w[i] = UInt32(message[offset]) << 24 |
                        UInt32(message[offset + 1]) << 16 |
                        UInt32(message[offset + 2]) << 8 |
                        UInt32(message[offset + 3])
            }
            
            for i in 16..<64 {
                let s0 = rightRotate(w[i-15], 7) ^ rightRotate(w[i-15], 18) ^ (w[i-15] >> 3)
                let s1 = rightRotate(w[i-2], 17) ^ rightRotate(w[i-2], 19) ^ (w[i-2] >> 10)
                w[i] = w[i-16] &+ s0 &+ w[i-7] &+ s1
            }
            
            var a = h[0], b = h[1], c = h[2], d = h[3]
            var e = h[4], f = h[5], g = h[6], hh = h[7]
            
            for i in 0..<64 {
                let S1 = rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)
                let ch = (e & f) ^ (~e & g)
                let temp1 = hh &+ S1 &+ ch &+ k[i] &+ w[i]
                let S0 = rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)
                let maj = (a & b) ^ (a & c) ^ (b & c)
                let temp2 = S0 &+ maj
                
                hh = g; g = f; f = e; e = d &+ temp1
                d = c; c = b; b = a; a = temp1 &+ temp2
            }
            
            h[0] = h[0] &+ a; h[1] = h[1] &+ b
            h[2] = h[2] &+ c; h[3] = h[3] &+ d
            h[4] = h[4] &+ e; h[5] = h[5] &+ f
            h[6] = h[6] &+ g; h[7] = h[7] &+ hh
        }
        
        return h.map { String(format: "%08x", $0) }.joined()
    }
    
    private static func rightRotate(_ value: UInt32, _ count: UInt32) -> UInt32 {
        return (value >> count) | (value << (32 - count))
    }
    
    /// XOR-based encryption (simplified — production would use AES-GCM).
    static func xorEncrypt(_ data: Data, key: Data) -> Data {
        var encrypted = [UInt8](repeating: 0, count: data.count)
        let keyBytes = [UInt8](key)
        let dataBytes = [UInt8](data)
        
        for i in 0..<data.count {
            encrypted[i] = dataBytes[i] ^ keyBytes[i % keyBytes.count]
        }
        
        return Data(encrypted)
    }
}

// MARK: - Keychain Engine

final class OmniKeychainSecurityEngine {
    
    private var store: [String: KeychainItem] = [:]
    private let encryptionKey: Data
    
    // Metrics
    private(set) var totalReads: Int = 0
    private(set) var totalWrites: Int = 0
    private(set) var totalDeletes: Int = 0
    private(set) var integrityChecks: Int = 0
    private(set) var integrityFailures: Int = 0
    
    init(encryptionKey: String = "omni-keychain-master-key-256bit") {
        self.encryptionKey = encryptionKey.data(using: .utf8)!
    }
    
    /// Store a value securely with encryption and integrity hash.
    func save(key: String, value: String,
              accessLevel: KeychainItem.AccessLevel = .whenUnlocked) -> KeychainResult<Void> {
        guard !key.isEmpty else {
            return .failure(.invalidKey("Key cannot be empty"))
        }
        guard let data = value.data(using: .utf8) else {
            return .failure(.encodingError("Failed to encode value"))
        }
        
        let encrypted = OmniCryptoUtils.xorEncrypt(data, key: encryptionKey)
        let hash = OmniCryptoUtils.sha256(data)
        
        let item = KeychainItem(
            key: key,
            data: encrypted,
            createdAt: store[key]?.createdAt ?? Date(),
            updatedAt: Date(),
            accessLevel: accessLevel,
            integrityHash: hash
        )
        
        store[key] = item
        totalWrites += 1
        return .success(())
    }
    
    /// Retrieve and decrypt a value, verifying integrity.
    func load(key: String) -> KeychainResult<String> {
        totalReads += 1
        
        guard let item = store[key] else {
            return .failure(.itemNotFound)
        }
        
        let decrypted = OmniCryptoUtils.xorEncrypt(item.data, key: encryptionKey)
        
        // Verify integrity
        integrityChecks += 1
        let currentHash = OmniCryptoUtils.sha256(decrypted)
        guard currentHash == item.integrityHash else {
            integrityFailures += 1
            return .failure(.hashMismatch)
        }
        
        guard let value = String(data: decrypted, encoding: .utf8) else {
            return .failure(.decodingError("Failed to decode decrypted data"))
        }
        
        return .success(value)
    }
    
    /// Delete a stored item.
    func delete(key: String) -> KeychainResult<Void> {
        guard store.removeValue(forKey: key) != nil else {
            return .failure(.itemNotFound)
        }
        totalDeletes += 1
        return .success(())
    }
    
    /// Check if a key exists.
    func contains(key: String) -> Bool {
        return store[key] != nil
    }
    
    /// Get all stored keys.
    var allKeys: [String] { Array(store.keys) }
    
    /// Total items in keychain.
    var itemCount: Int { store.count }
    
    // MARK: - Diagnostics
    
    func diagnostics() -> [String: Any] {
        return [
            "engine": "OmniKeychainSecurityEngine",
            "layer": "Swift UI",
            "total_items": store.count,
            "total_reads": totalReads,
            "total_writes": totalWrites,
            "total_deletes": totalDeletes,
            "integrity_checks": integrityChecks,
            "integrity_failures": integrityFailures,
            "learned_logic": [
                "apple-keychain-services-api",
                "sha256-fips180-4-compression",
                "xor-cipher-encryption",
                "integrity-hash-verification",
                "access-level-security-policy",
                "result-monadic-error-handling",
                "data-at-rest-encryption",
                "right-rotate-bitops"
            ]
        ]
    }
}
