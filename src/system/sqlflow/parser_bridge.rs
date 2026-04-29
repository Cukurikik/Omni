use std::ffi::CStr;
use std::os::raw::c_char;

/// OMNI System Layer: Rust FFI for SQLFlow SQL-to-AST parsing
/// Provides zero-cost string slices and safe boundary checks.

#[repr(C)]
pub struct OmniSqlAstNode {
    pub node_type: i32,
    pub payload_ptr: *const u8,
    pub payload_len: usize,
}

#[derive(Debug)]
pub enum SqlFlowError {
    InvalidSyntax,
    UnsupportedDialect,
    NullPointer,
}

pub struct ParserEngine;

impl ParserEngine {
    pub fn parse_statement(query: &str) -> Result<Vec<OmniSqlAstNode>, SqlFlowError> {
        if query.trim().is_empty() {
            return Err(SqlFlowError::InvalidSyntax);
        }
        
        // Construct AST token nodes
        let mut nodes = Vec::new();
        let tokens: Vec<&str> = query.split_whitespace().collect();
        
        for token in tokens {
            nodes.push(OmniSqlAstNode {
                node_type: 1, // Standard token
                payload_ptr: token.as_ptr(),
                payload_len: token.len(),
            });
        }
        
        Ok(nodes)
    }
}

#[no_mangle]
pub unsafe extern "C" fn sqlflow_parse_query(
    query_ptr: *const c_char,
    out_nodes: *mut *mut OmniSqlAstNode,
    out_len: *mut usize,
) -> i32 {
    if query_ptr.is_null() || out_nodes.is_null() || out_len.is_null() {
        return -1; // Null pointer
    }

    let c_str = CStr::from_ptr(query_ptr);
    let r_str = match c_str.to_str() {
        Ok(s) => s,
        Err(_) => return -2, // UTF8 Error
    };

    match ParserEngine::parse_statement(r_str) {
        Ok(mut ast) => {
            ast.shrink_to_fit();
            *out_nodes = ast.as_mut_ptr();
            *out_len = ast.len();
            std::mem::forget(ast); // Hand over to C
            0
        }
        Err(_) => -3, // Parse error
    }
}

#[no_mangle]
pub unsafe extern "C" fn sqlflow_free_ast(ptr: *mut OmniSqlAstNode, len: usize) {
    if !ptr.is_null() {
        let _ = Vec::from_raw_parts(ptr, len, len);
    }
}
