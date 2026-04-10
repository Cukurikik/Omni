use super::OmniRequest;
use std::collections::HashMap;

pub struct HttpParser;

impl HttpParser {
    pub fn parse(raw_data: &[u8]) -> Option<OmniRequest> {
        let request_str = std::str::from_utf8(raw_data).ok()?;
        let mut lines = request_str.lines();
        
        let request_line = lines.next()?;
        let mut parts = request_line.split_whitespace();
        let method = parts.next()?.to_string();
        let path = parts.next()?.to_string();
        
        let mut headers = HashMap::new();
        let mut is_body = false;
        let mut body = String::new();
        
        for line in lines {
            if is_body {
                body.push_str(line);
                body.push('\n');
                continue;
            }
            if line.is_empty() {
                is_body = true;
                continue;
            }
            if let Some((k, v)) = line.split_once(": ") {
                headers.insert(k.to_string(), v.to_string());
            }
        }
        
        Some(OmniRequest {
            method,
            path,
            headers,
            body,
        })
    }
}
