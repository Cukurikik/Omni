// ==========================================
// 🛡️ OMNI-LAND: MILITARY-GRADE CRYPTOGRAPHY
// ==========================================
// AES-256-GCM, SHA-256, SHA-512, HMAC, PBKDF2
// Semua menggunakan Go crypto/ stdlib (hardware-accelerated AES-NI)
//
// IMPORT: import { crypto } from 'omni/crypto';
// ==========================================

declare const OmniNative: {
    syscall: (command: string, args: Record<string, unknown>) => Record<string, unknown>;
};

// ==========================================
// HASHING
// ==========================================

/**
 * Hash data menggunakan algoritma tertentu.
 * @param algo - "sha256" | "sha512" | "md5" | "sha1"
 * @param data - String yang akan di-hash
 * @returns Hex string dari hash
 */
export function hash(algo: string, data: string): string {
    const res = OmniNative.syscall("crypto_hash", { algo, payload: data });
    if (res.error) throw new Error(`[OMNI-CRYPTO] Hash gagal: ${res.error}`);
    return res.result as string;
}

/**
 * HMAC signing — buat message authentication code.
 * @param algo - "sha256" | "sha512"
 * @param data - Data yang akan di-sign
 * @param secret - Kunci rahasia
 */
export function hmacSign(algo: string, data: string, secret: string): string {
    const res = OmniNative.syscall("crypto_hmac", { algo, data, secret });
    if (res.error) throw new Error(`[OMNI-CRYPTO] HMAC gagal: ${res.error}`);
    return res.result as string;
}

/**
 * HMAC verify — verifikasi signature.
 */
export function hmacVerify(algo: string, data: string, secret: string, signature: string): boolean {
    const res = OmniNative.syscall("crypto_hmac_verify", { algo, data, secret, signature });
    return res.result as boolean;
}

// ==========================================
// AES-256-GCM ENCRYPTION (Standar Perbankan)
// ==========================================

/**
 * Enkripsi AES-256-GCM.
 * @param plainText - Teks yang akan dienkripsi
 * @param secretKey - Kunci 32-byte (akan di-hash ke 256-bit jika lebih pendek)
 * @returns Base64-encoded ciphertext (nonce || ciphertext || tag)
 */
export function encryptAES(plainText: string, secretKey: string): string {
    const res = OmniNative.syscall("crypto_encrypt_aes", { plainText, secretKey });
    if (res.error) throw new Error(`[OMNI-CRYPTO] Enkripsi gagal: ${res.error}`);
    return res.cipherText as string;
}

/**
 * Dekripsi AES-256-GCM.
 * @param cipherText - Base64-encoded ciphertext dari encryptAES()
 * @param secretKey - Kunci yang sama digunakan saat enkripsi
 */
export function decryptAES(cipherText: string, secretKey: string): string {
    const res = OmniNative.syscall("crypto_decrypt_aes", { cipherText, secretKey });
    if (res.error) throw new Error(`[OMNI-CRYPTO] Dekripsi gagal: ${res.error}`);
    return res.plainText as string;
}

// ==========================================
// RANDOM GENERATION
// ==========================================

/**
 * Generate UUID v4 yang aman secara kriptografis.
 */
export function randomUUID(): string {
    const res = OmniNative.syscall("crypto_uuid", {});
    return res.uuid as string;
}

/**
 * Generate random bytes (hex-encoded).
 * @param size - Jumlah byte random yang diinginkan
 */
export function randomBytes(size: number): string {
    const res = OmniNative.syscall("crypto_random", { size });
    return res.bytes as string;
}

/**
 * Generate random integer dalam range [min, max).
 */
export function randomInt(min: number, max: number): number {
    const res = OmniNative.syscall("crypto_random_int", { min, max });
    return res.result as number;
}

// ==========================================
// KEY DERIVATION
// ==========================================

/**
 * PBKDF2 key derivation — ubah password menjadi encryption key.
 * @param password - Password mentah
 * @param salt - Salt (gunakan randomBytes untuk generate)
 * @param iterations - Jumlah iterasi (minimal 100000)
 * @param keyLen - Panjang key output dalam byte
 */
export function pbkdf2(password: string, salt: string, iterations: number, keyLen: number): string {
    const res = OmniNative.syscall("crypto_pbkdf2", { password, salt, iterations, keyLen });
    if (res.error) throw new Error(`[OMNI-CRYPTO] PBKDF2 gagal: ${res.error}`);
    return res.result as string;
}

/**
 * Bcrypt hash password (untuk penyimpanan di database).
 * @param password - Password yang akan di-hash
 * @param cost - Cost factor (default 12)
 */
export function bcryptHash(password: string, cost?: number): string {
    const res = OmniNative.syscall("crypto_bcrypt_hash", { password, cost: cost ?? 12 });
    if (res.error) throw new Error(`[OMNI-CRYPTO] Bcrypt gagal: ${res.error}`);
    return res.hash as string;
}

/**
 * Verifikasi password terhadap bcrypt hash.
 */
export function bcryptVerify(password: string, hashStr: string): boolean {
    const res = OmniNative.syscall("crypto_bcrypt_verify", { password, hash: hashStr });
    return res.result as boolean;
}

// ==========================================
// DIGITAL SIGNATURES
// ==========================================

/**
 * Generate ED25519 keypair untuk digital signature.
 * @returns { publicKey, privateKey } sebagai hex strings
 */
export function generateKeyPair(): { publicKey: string; privateKey: string } {
    const res = OmniNative.syscall("crypto_generate_keypair", {});
    if (res.error) throw new Error(`[OMNI-CRYPTO] Keypair gagal: ${res.error}`);
    return res.result as { publicKey: string; privateKey: string };
}

/**
 * Sign data dengan ED25519 private key.
 */
export function sign(data: string, privateKey: string): string {
    const res = OmniNative.syscall("crypto_sign", { data, privateKey });
    if (res.error) throw new Error(`[OMNI-CRYPTO] Signing gagal: ${res.error}`);
    return res.signature as string;
}

/**
 * Verify signature dengan ED25519 public key.
 */
export function verify(data: string, signature: string, publicKey: string): boolean {
    const res = OmniNative.syscall("crypto_verify", { data, signature, publicKey });
    return res.result as boolean;
}

export const crypto = {
    hash,
    hmacSign,
    hmacVerify,
    encryptAES,
    decryptAES,
    randomUUID,
    randomBytes,
    randomInt,
    pbkdf2,
    bcryptHash,
    bcryptVerify,
    generateKeyPair,
    sign,
    verify,
};

export default crypto;
