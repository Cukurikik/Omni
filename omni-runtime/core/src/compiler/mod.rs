pub mod ir;
pub mod ast;
pub mod lexer;
pub mod parser;
pub mod generator;
pub mod transpiler;
pub mod optimizer;
pub mod ffi;
pub mod nexus;
pub mod backend; // TARGET JIT/AOT/WASM
pub mod semantic;

pub use ir::*;
pub use transpiler::*;
pub use optimizer::*;
pub use ffi::*;
pub use backend::*;
pub use semantic::*;

