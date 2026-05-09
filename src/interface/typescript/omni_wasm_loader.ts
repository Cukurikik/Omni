// OMNI MOTHER: WebAssembly Loader (Production Grade)
// Loads the Omni C/Rust core into the browser for local ML inference.

export class OmniWasmLoader {
    private instance: WebAssembly.Instance | null = null;

    public async load(wasmPath: string): Promise<void> {
        console.log(`[OMNI WASM] Fetching binary from ${wasmPath}...`);
        try {
            const response = await fetch(wasmPath);
            const bytes = await response.arrayBuffer();
            const { instance } = await WebAssembly.instantiate(bytes, {
                env: {
                    consoleLog: (arg: number) => console.log(arg)
                }
            });
            this.instance = instance;
            console.log("[OMNI WASM] Engine loaded successfully.");
        } catch (e) {
            console.error("[OMNI WASM] Failed to load binary:", e);
        }
    }

    public isReady(): boolean {
        return this.instance !== null;
    }
}
