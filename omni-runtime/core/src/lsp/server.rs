
use serde_json::Value;
use std::io::{self, BufRead, Read, Write};
use std::sync::{Arc, Mutex};
use super::uasg::{UnifiedAbstractSyntaxGraph, UasgNode, UasgNodeType, UasgType};
use super::type_mapper::SemanticTypeMapper;

pub struct OmniLspServer {
    uasg: Arc<Mutex<UnifiedAbstractSyntaxGraph>>,
}

impl OmniLspServer {
    pub fn new(uasg: Arc<Mutex<UnifiedAbstractSyntaxGraph>>) -> Self {
        Self { uasg }
    }

    pub fn run_stdio_loop(&self) {
        let stdin = io::stdin();
        let mut stdout = io::stdout();
        let mut handle = stdin.lock();

        eprintln!("🚀 OMNI-LSP Server dimulai via STDIO");

        loop {
            let mut header = String::new();
            if handle.read_line(&mut header).unwrap() == 0 { break; } // EOF
            if header.trim().is_empty() { continue; }

            // Analisis Format Header: Content-Length: <size>\r\n
            if header.starts_with("Content-Length:") {
                let len_str = header.trim_start_matches("Content-Length:").trim();
                let length: usize = len_str.parse().unwrap_or(0);
                
                // Read \r\n
                let mut empty_line = String::new();
                handle.read_line(&mut empty_line).unwrap();

                // Read Content
                let mut content = vec![0; length];
                handle.read_exact(&mut content).unwrap();

                if let Ok(request) = serde_json::from_slice::<Value>(&content) {
                    let response = self.handle_request(request);
                    if let Some(resp) = response {
                        let resp_str = serde_json::to_string(&resp).unwrap();
                        let msg = format!("Content-Length: {}\r\n\r\n{}", resp_str.len(), resp_str);
                        stdout.write_all(msg.as_bytes()).unwrap();
                        stdout.flush().unwrap();
                    }
                }
            }
        }
    }

    fn handle_request(&self, req: Value) -> Option<Value> {
        let method = req["method"].as_str().unwrap_or("");
        let id = req["id"].clone();

        match method {
            "initialize" => {
                Some(serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "capabilities": {
                            "textDocumentSync": 1,
                            "hoverProvider": true,
                            "completionProvider": { "resolveProvider": false },
                            "definitionProvider": true
                        }
                    }
                }))
            },
            "textDocument/hover" => {
                // Mock respons hover cerdas: 
                // Misal IDE mencari token di posisi kursor, kita cek UASG.
                let _uri = req["params"]["textDocument"]["uri"].as_str().unwrap_or("");
                let _uasg_lock = self.uasg.lock().unwrap();
                
                // --- Dummy Mock Data untuk UASG Node ---
                let mock_node = UasgNode {
                    id: "rust::omni_matrix::encrypt".to_string(),
                    original_lang: "rust".to_string(),
                    location_file: "src/matrix.rs".to_string(),
                    location_line: 42,
                    node_type: UasgNodeType::Function { 
                        params: vec![("data".to_string(), UasgType::RawPointer)], 
                        return_type: UasgType::Result(Box::new(UasgType::String), Box::new(UasgType::String)),
                        is_async: false 
                    }
                };

                let lang_client = "typescript"; // Misalnya editor lagi di TypeScript
                
                // Mengkonversi ke TS Types
                let mut signature = String::new();
                if let UasgNodeType::Function { ref params, ref return_type, .. } = mock_node.node_type {
                    let ts_param_type = SemanticTypeMapper::translate_to(lang_client, &params[0].1);
                    let ts_ret_type = SemanticTypeMapper::translate_to(lang_client, return_type);
                    signature = format!("function encrypt(data: {}): {}", ts_param_type, ts_ret_type);
                }

                // Mengecek Leak Memory
                let mut warnings = String::new();
                if let UasgNodeType::Function { ref params, .. } = mock_node.node_type {
                    if let Some(warning) = SemanticTypeMapper::check_memory_leak_risk(lang_client, &mock_node.original_lang, &params[0].1) {
                        warnings = format!("\n\n**⚠️ OMNI Linter:**\n{}", warning);
                    }
                }

                let hover_content = format!(
                    "**OMNI-LSP Cross-Language Insight**\n\n```{}\n{}\n```\n_Source: {} (Language: {})_\n\n_Performance Cost: O(N) - SIMD Accelerated_{}",
                    lang_client, signature, mock_node.location_file, mock_node.original_lang, warnings
                );

                Some(serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "contents": hover_content
                    }
                }))
            },
            "textDocument/definition" => {
                // Menghasilkan "Jump to Definition" menembus bahasa
                Some(serde_json::json!({
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "uri": "file:///c:/Users/IKYY/Downloads/Omni/omni-runtime/core/src/matrix.rs",
                        "range": {
                            "start": { "line": 41, "character": 0 },
                            "end": { "line": 41, "character": 10 }
                        }
                    }
                }))
            },
            _ => None
        }
    }
}
