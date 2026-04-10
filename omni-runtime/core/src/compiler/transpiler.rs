use super::ir::OmniIR;
use super::backend::{LLVMEmitter, WasmJsEmitter, OmniVMEngine};

pub struct OmniBinaryArtifact {
    pub llvm_ir: String,
    pub wasm_js: String,
    pub omni_vm: String,
}

pub struct OmniTranspiler {
    ir: OmniIR,
}

impl OmniTranspiler {
    pub fn new(ir: OmniIR) -> Self {
        Self { ir }
    }

    pub fn orchestrate(&self) -> OmniBinaryArtifact {
        println!("[OMNI THE FORGE MASTER] Initiating TRI-TARGET Transpilation Sequence...");

        let llvm_emitter = LLVMEmitter::new();
        let wasm_js_emitter = WasmJsEmitter::new();
        let vm_engine = OmniVMEngine::new();

        OmniBinaryArtifact {
            llvm_ir: llvm_emitter.emit(&self.ir),
            wasm_js: wasm_js_emitter.emit(&self.ir),
            omni_vm: vm_engine.emit(&self.ir),
        }
    }
}
