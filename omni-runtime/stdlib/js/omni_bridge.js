// ============================================================
// OMNI JavaScript Bridge — V8 MicroIsolate Native API
// ============================================================
// KITA TIDAK MENGGUNAKAN Node.js, Bun, atau Deno.
// Script ini dijalankan oleh OMNI V8 MicroIsolate (Phase 8-10).
// Akses ke memori kernel Rust melalui __omni_ffi yang sudah
// ter-inject di global scope V8 Isolate oleh engine kita.
// ============================================================

/**
 * Mengeksekusi fungsi native OMNI dari dalam konteks V8.
 * __omni_ffi sudah di-bind ke global scope oleh OmniV8Runtime.
 *
 * @param {string} functionName - Nama fungsi di registry OMNI
 * @param {ArrayBuffer} dataBuffer - Data mentah (zero-copy via SharedArrayBuffer)
 * @returns {ArrayBuffer} - Pointer result dari kernel Rust
 */
function executeOmniFunction(functionName, dataBuffer) {
  // __omni_ffi di-inject oleh src/runtime/v8_micro_isolate.rs
  if (typeof __omni_ffi === 'undefined') {
    throw new Error('[OMNI-E101] V8 MicroIsolate belum terinisialisasi. Jalankan via `omni run`.');
  }
  return __omni_ffi(functionName, dataBuffer);
}

/**
 * Membuat OmniBuffer baru dari dalam V8 tanpa serialisasi.
 * Menggunakan SharedArrayBuffer untuk zero-copy antara JS ↔ Rust.
 */
function createOmniBuffer(sizeBytes) {
  if (typeof __omni_buffer_alloc === 'undefined') {
    throw new Error('[OMNI-E102] Buffer allocator tidak tersedia di isolate ini.');
  }
  return __omni_buffer_alloc(sizeBytes);
}

/**
 * Spawn goroutine OMNI dari konteks JavaScript.
 * Delegasi ke OmniEventLoop (Phase 12) melalui binding global.
 */
function spawnOmniTask(taskName, payload) {
  if (typeof __omni_spawn === 'undefined') {
    throw new Error('[OMNI-E103] OmniEventLoop belum aktif.');
  }
  return __omni_spawn(taskName, payload);
}

// Export ke OMNI module system (bukan CommonJS/ESM)
globalThis.OmniBridge = {
  execute: executeOmniFunction,
  allocBuffer: createOmniBuffer,
  spawn: spawnOmniTask,
};
