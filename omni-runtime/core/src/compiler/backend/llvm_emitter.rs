use super::super::ir::{OmniIR, OmniInstruction};
use super::super::ffi::ir_type_to_llvm;
use crate::parser::{Statement, Expr};

pub struct LLVMEmitter;

impl LLVMEmitter {
    pub fn new() -> Self {
        Self
    }

    pub fn emit(&self, ir: &OmniIR) -> String {
        let mut llvm_assembly = String::new();
        llvm_assembly.push_str("; ===============================================\n");
        llvm_assembly.push_str("; OMNI-LANG LLVM IR (Bare-Metal DNA)\n");
        llvm_assembly.push_str("; Target: x86_64-pc-windows-msvc / aarch64\n");
        llvm_assembly.push_str("; ===============================================\n\n");

        // First pass: emit all FFI declarations at the top
        for instruction in &ir.instructions {
            if let OmniInstruction::FFIDeclare { name, lib, language, params, ret, gil_safe } = instruction {
                llvm_assembly.push_str(&format!("; @ffi(lib = \"{}\", language = \"{}\"{})\n", 
                    lib, language, if *gil_safe { ", gil_safe = true" } else { "" }));
                
                let param_types: Vec<String> = params.iter()
                    .map(|p| ir_type_to_llvm(p))
                    .collect();
                
                llvm_assembly.push_str(&format!("declare {} @{}({})\n\n", 
                    ir_type_to_llvm(ret),
                    name,
                    param_types.join(", ")
                ));

                // Python GIL helpers
                if language == "Python" {
                    llvm_assembly.push_str("declare i32 @PyGILState_Ensure()\n");
                    llvm_assembly.push_str("declare void @PyGILState_Release(i32)\n\n");
                }
            }
        }

        // Second pass: emit all other instructions
        for instruction in &ir.instructions {
            match instruction {
                OmniInstruction::SimdMultiply { dest, left_matrix_ptr, right_matrix_ptr } => {
                    llvm_assembly.push_str(&format!("  %{} = call fast double @llvm.x86.avx.mul (<4 x double> %{}, <4 x double> %{})\n", dest, left_matrix_ptr, right_matrix_ptr));
                }
                OmniInstruction::MemoryAlloc { dest, size_bytes } => {
                    llvm_assembly.push_str(&format!("  %{} = alloca i8, i32 {}\n", dest, size_bytes));
                }
                OmniInstruction::MemoryFree { ptr } => {
                    llvm_assembly.push_str(&format!("  call void @free(i8* %{})\n", ptr));
                }
                OmniInstruction::Add { dest, left, right } => {
                    llvm_assembly.push_str(&format!("  %{} = fadd double %{}, %{}\n", dest, left, right));
                }
                OmniInstruction::LoadConstantInt { dest, value } => {
                    llvm_assembly.push_str(&format!("  %{} = add i64 0, {}\n", dest, value));
                }
                OmniInstruction::LoadConstantFloat { dest, value } => {
                    llvm_assembly.push_str(&format!("  %{} = fadd double 0.0, {}\n", dest, value));
                }
                OmniInstruction::FFICall { dest, func_name, args } => {
                    let args_str: Vec<String> = args.iter().enumerate()
                        .map(|(_i, a)| format!("i64 %{}", a))
                        .collect();
                    llvm_assembly.push_str(&format!("  %{} = call i64 @{}({})\n", 
                        dest, func_name, args_str.join(", ")));
                }
                OmniInstruction::FFIDeclare { .. } => {}
                _ => {}
            }
        }

        llvm_assembly
    }

    pub fn emit_ast(&self, statements: &[Statement]) -> String {
        let mut llvm_assembly = String::new();
        llvm_assembly.push_str("; ===============================================\n");
        llvm_assembly.push_str("; OMNI-PRIME The Realism Protocol (LLVM IR Direct Emit)\n");
        llvm_assembly.push_str("; Target: x86_64-pc-windows-msvc / aarch64\n");
        llvm_assembly.push_str("; ===============================================\n\n");

        llvm_assembly.push_str("declare void @omni_spawn(i8* %task_ptr)\n");
        llvm_assembly.push_str("declare i64 @omni_await(i8* %task_ptr)\n");
        llvm_assembly.push_str("declare void @omni_polyglot_dispatch(i8* %lang, i8* %code)\n\n");

        // Forward declare functions
        for stmt in statements {
            if let Statement::FunctionDeclaration(fn_decl) = stmt {
                llvm_assembly.push_str(&format!("define i32 @{}() {{\nentry:\n", fn_decl.name));
                Self::emit_block(&mut llvm_assembly, &fn_decl.body);
                llvm_assembly.push_str("  ret i32 0\n}\n\n");
            }
        }

        llvm_assembly.push_str("define i32 @main() {\nentry:\n");
        Self::emit_block(&mut llvm_assembly, statements);
        llvm_assembly.push_str("  ret i32 0\n}\n");
        
        llvm_assembly
    }

    fn emit_block(llvm_assembly: &mut String, statements: &[Statement]) {
        let mut reg_counter = 1;
        for stmt in statements {
            match stmt {
                Statement::LetBinding { name, value } => {
                    llvm_assembly.push_str(&format!("  ; let {} = ...\n", name));
                    match value {
                        Expr::Spawn(inner) => {
                            if let Expr::Call { callee, .. } = &**inner {
                                if let Expr::Identifier(_func_name) = &**callee {
                                    llvm_assembly.push_str(&format!("  %{} = alloca i8, i32 32\n", reg_counter));
                                    llvm_assembly.push_str(&format!("  call void @omni_spawn(i8* %{})\n", reg_counter));
                                    reg_counter += 1;
                                }
                            }
                        }
                        Expr::IntLiteral(val) => {
                            llvm_assembly.push_str(&format!("  %{} = alloca i64\n", name));
                            llvm_assembly.push_str(&format!("  store i64 {}, i64* %{}\n", val, name));
                        }
                        Expr::NumberLiteral(val) => {
                            llvm_assembly.push_str(&format!("  %{} = alloca double\n", name));
                            llvm_assembly.push_str(&format!("  store double {}, double* %{}\n", val, name));
                        }
                        Expr::PolyglotNode(poly) => {
                            llvm_assembly.push_str(&format!("  ; [Polyglot: {}] Injecting external bindings -> {}\n", poly.language, name));
                            let lang_ptr = format!("@.str.lang.{}", reg_counter);
                            let code_ptr = format!("@.str.code.{}", reg_counter);
                            llvm_assembly.push_str(&format!("  call void @omni_polyglot_dispatch(i8* {}, i8* {})\n", lang_ptr, code_ptr));
                            reg_counter += 1;
                        }
                        _ => {}
                    }
                }
                Statement::ExprStmt(expr) => {
                    match expr {
                        Expr::Await(inner) => {
                            if let Expr::Identifier(task_name) = &**inner {
                                llvm_assembly.push_str(&format!("  %{} = call i64 @omni_await(i8* %{})\n", reg_counter, task_name));
                                reg_counter += 1;
                            }
                        }
                        Expr::PolyglotNode(poly) => {
                            llvm_assembly.push_str(&format!("  ; [Polyglot: {}]\n", poly.language));
                            llvm_assembly.push_str(&format!("  call void @omni_polyglot_dispatch(i8* null, i8* null)\n"));
                        }
                        Expr::Call { callee, .. } => {
                            if let Expr::Identifier(func_name) = &**callee {
                                llvm_assembly.push_str(&format!("  %{} = call i32 @{}()\n", reg_counter, func_name));
                                reg_counter += 1;
                            }
                        }
                        _ => {}
                    }
                }
                _ => {}
            }
        }
    }
}

