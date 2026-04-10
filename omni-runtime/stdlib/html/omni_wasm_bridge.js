// ============================================================
// OMNI HTML/WASM Bridge — Browser UI Nexus
// ============================================================
// Layer: UI (Browser, Progressive Web App)
// Dijalankan oleh browser WebAssembly runtime — BUKAN Node.js.
// File ini di-bundle bersama WASM binary oleh `omni build --wasm`.
// ============================================================

/**
 * OmniWasmBridge menghubungkan browser DOM ke kernel OMNI
 * yang dikompilasi menjadi WebAssembly.
 */
class OmniWasmBridge {
  constructor() {
    this.wasm = null;
    this.memory = null;
    this.ready = false;
  }

  /**
   * Inisialisasi WASM module dari binary yang dikompilasi oleh OMNI.
   * @param {string} wasmUrl - Path ke .wasm file (dari `omni build --target wasm32`)
   */
  async init(wasmUrl) {
    const response = await fetch(wasmUrl);
    const bytes = await response.arrayBuffer();

    const importObject = {
      env: {
        // Callback dari Rust ke JS (event bridge)
        __omni_js_callback: (ptr, len) => {
          const data = new Uint8Array(this.memory.buffer, ptr, len);
          this._onKernelCallback(data);
        },
      },
    };

    const { instance } = await WebAssembly.instantiate(bytes, importObject);
    this.wasm = instance.exports;
    this.memory = instance.exports.memory;
    this.ready = true;
  }

  /**
   * Eksekusi fungsi OMNI di dalam browser WASM sandbox.
   * @param {ArrayBuffer} dataBuffer - Data mentah
   * @returns {Uint8Array} - Result dari kernel
   */
  execute(dataBuffer) {
    if (!this.ready) {
      throw new Error('[OMNI-E1001] WASM belum terinisialisasi. Panggil init() dulu.');
    }

    const inputBytes = new Uint8Array(dataBuffer);
    const inputLen = inputBytes.length;

    // Alokasi di WASM linear memory
    const inputPtr = this.wasm.__omni_buffer_alloc(inputLen);
    const wasmMemory = new Uint8Array(this.memory.buffer);
    wasmMemory.set(inputBytes, inputPtr);

    // Panggil __omni_ffi di dalam WASM
    const resultPtr = this.wasm.__omni_ffi(inputPtr, inputLen);

    // Baca result (header 8 bytes: 4 byte len + 4 byte status)
    const resultView = new DataView(this.memory.buffer, resultPtr, 8);
    const resultLen = resultView.getUint32(0, true);
    const resultStatus = resultView.getUint32(4, true);

    if (resultStatus !== 0) {
      throw new Error(`[OMNI-E${resultStatus}] Kernel WASM error`);
    }

    return new Uint8Array(this.memory.buffer, resultPtr + 8, resultLen);
  }

  /**
   * Handler untuk event dari kernel → browser
   * Override ini untuk menangkap real-time updates.
   */
  _onKernelCallback(data) {
    // Default: dispatch CustomEvent ke DOM
    const event = new CustomEvent('omni:callback', {
      detail: { data: data },
    });
    document.dispatchEvent(event);
  }
}

// Export ke global browser scope
if (typeof window !== 'undefined') {
  window.OmniWasmBridge = OmniWasmBridge;
}
