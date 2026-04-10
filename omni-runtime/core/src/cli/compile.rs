// ==========================================
// ⚡ OMNI-COMPILE: Source → AST → LLVM IR Pipeline
// ==========================================
// Membaca file .omni, memparsing ke AST via PEG/Pest,
// menjalankan Semantic Analysis, lalu meng-emit LLVM IR.
// ==========================================

use crate::parser::{parse_omni_source, Program};
use crate::semantic::SemanticAnalyzer;
use crate::compiler::backend::llvm_emitter::LLVMEmitter;
use std::fs;

pub fn run(args: &[String]) {
    let file_path = if args.is_empty() {
        println!("Usage: omni compile <file.omni> [--emit-ir] [--emit-ast]");
        return;
    } else {
        &args[0]
    };

    let emit_ir = args.iter().any(|a| a == "--emit-ir");
    let emit_ast = args.iter().any(|a| a == "--emit-ast");

    println!("⚡ [OMNI-COMPILE] Compiling: {}", file_path);

    // Step 1: Read source file
    let source = match fs::read_to_string(file_path) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("❌ [FATAL] Cannot read file '{}': {}", file_path, e);
            return;
        }
    };

    // Step 2: Parse to AST
    println!("📖 [PHASE 1] Parsing source via PEG grammar...");
    let program = match parse_omni_source(&source) {
        Ok(p) => {
            println!("  ✅ AST constructed: {} top-level statements", p.body.len());
            p
        }
        Err(e) => {
            eprintln!("❌ [PARSE ERROR] {}", e);
            return;
        }
    };

    // Step 2b: Optional AST dump
    if emit_ast {
        println!("\n--- AST DUMP ---");
        for (i, stmt) in program.body.iter().enumerate() {
            println!("  [{}] {:?}", i, stmt);
        }
        println!("--- END AST ---\n");
    }

    // Step 3: Semantic Analysis
    println!("⚖️  [PHASE 2] Running Semantic Analysis...");
    let mut analyzer = SemanticAnalyzer::new();
    match analyzer.analyze(&program.body) {
        Ok(()) => println!("  ✅ Semantic analysis passed."),
        Err(e) => {
            eprintln!("❌ [SEMANTIC ERROR] {}", e);
            return;
        }
    }

    // Step 4: LLVM IR Generation
    println!("🔧 [PHASE 3] Generating LLVM IR...");
    let emitter = LLVMEmitter::new();
    let llvm_ir = emitter.emit_ast(&program.body);

    // Count IR lines
    let ir_lines = llvm_ir.lines().count();
    println!("  ✅ Generated {} lines of LLVM IR.", ir_lines);

    // Step 5: Output
    if emit_ir {
        println!("\n--- LLVM IR OUTPUT ---");
        println!("{}", llvm_ir);
        println!("--- END LLVM IR ---");
    }

    // Write .ll file
    let output_path = file_path.replace(".omni", ".ll");
    match fs::write(&output_path, &llvm_ir) {
        Ok(()) => {
            println!("📄 [OUTPUT] LLVM IR written to: {}", output_path);
        }
        Err(e) => {
            eprintln!("❌ [WRITE ERROR] Failed to write {}: {}", output_path, e);
        }
    }

    println!("🎉 [OMNI-COMPILE] Compilation complete!");
}
