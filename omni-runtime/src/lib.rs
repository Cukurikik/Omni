pub mod optimizer {
    pub mod llvm_passes;
}

use optimizer::llvm_passes::OmniVectorizer;

// FFI exposure untuk Go Gateway
#[no_mangle]
pub extern "C" fn omni_jit_compile(ast_ptr: *const u8, len: usize) -> i32 {
    if ast_ptr.is_null() || len == 0 {
        return -1;
    }

    // Zero-Copy Slice Reinterpretation
    let ir_slice = unsafe { std::slice::from_raw_parts(ast_ptr, len) };
    
    let mut vectorizer = OmniVectorizer::new();
    
    match vectorizer.execute_passes(ir_slice) {
        Ok(_) => {
            // Simulasi Neural JIT Feedback loop untuk telemetry
            vectorizer.train_neural_cache("neural_net.forward", 15.2);
            0 // Success
        },
        Err(_) => -2, // Code generation failed
    }
}
