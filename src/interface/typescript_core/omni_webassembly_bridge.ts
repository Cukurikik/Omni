// OMNI Interface Layer: WebAssembly Bridge
export class OmniWasmBridge {
    public async loadWasm(url: string) {
        const response = await fetch(url);
        const buffer = await response.arrayBuffer();
        const module = await WebAssembly.instantiate(buffer);
        return module;
    }
}
