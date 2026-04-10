use super::super::ir::{OmniIR, OmniInstruction};

pub struct WasmJsEmitter;

impl WasmJsEmitter {
    pub fn new() -> Self {
        Self
    }

    pub fn emit(&self, ir: &OmniIR) -> String {
        let mut js_code = String::new();
        js_code.push_str("// ===============================================\n");
        js_code.push_str("// OMNI-LANG WASM/JS TRANSPILER (Web & UI DNA)\n");
        js_code.push_str("// Target: V8 / WebKit / Blink / DOM Reactivity\n");
        js_code.push_str("// ===============================================\n\n");

        js_code.push_str("export function OmniAppBoundary() {\n");
        
        for instruction in &ir.instructions {
            match instruction {
                // Konversi UI ke React/DOM layer
                OmniInstruction::AllocRenderTree { dest, tag } => {
                    js_code.push_str(&format!("  const {} = document.createElement('{}');\n", dest, tag));
                }
                OmniInstruction::SpawnStateMachine { dest, state_id, func_ptr } => {
                    js_code.push_str(&format!("  const {} = OmniRuntime.spawnGoroutine({}, {});\n", dest, state_id, func_ptr));
                }
                OmniInstruction::LoadConstantInt { dest, value } => {
                    js_code.push_str(&format!("  const {} = {};\n", dest, value));
                }
                OmniInstruction::LoadConstantFloat { dest, value } => {
                    js_code.push_str(&format!("  const {} = {};\n", dest, value));
                }
                OmniInstruction::Add { dest, left, right } => {
                    js_code.push_str(&format!("  const {} = {} + {};\n", dest, left, right));
                }
                OmniInstruction::MonomorphizedCall { dest, func_name_mangled, args } => {
                    js_code.push_str(&format!("  const {} = {}({});\n", dest, func_name_mangled, args.join(", ")));
                }
                OmniInstruction::MemoryAlloc { dest, size_bytes } => {
                    js_code.push_str(&format!("  const {} = OmniRuntime.malloc({});\n", dest, size_bytes));
                }
                OmniInstruction::MemoryFree { ptr } => {
                    js_code.push_str(&format!("  OmniRuntime.free({});\n", ptr));
                }
                _ => {}
            }
        }
        
        js_code.push_str("  return { status: 'mounted' };\n");
        js_code.push_str("}\n");

        js_code
    }
}
