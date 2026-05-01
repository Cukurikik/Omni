/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// High-Speed Code Privacy Redactor.
/// A deterministic finite automaton (DFA) pipeline to redact API keys and PII from AI coding sessions.

use std::sync::Arc;
use regex::Regex;

#[derive(Debug, PartialEq)]
pub enum RedactionError {
    EmptyPayload,
    InvalidRegexCompilation,
}

pub struct CodeclawRedactor {
    // We use precompiled regex for extreme throughput
    patterns: Vec<Regex>,
    redaction_mask: String,
}

impl CodeclawRedactor {
    pub fn new(mask: &str) -> Result<Self, RedactionError> {
        let raw_patterns = vec![
            // AWS Keys
            r"(?i)AKIA[0-9A-Z]{16}",
            // Generic Bearer/API Tokens (High entropy hex/base64 strings near 'token' or 'key')
            r"(?i)(?:key|token|secret|password|api[_-]?key)\s*[:=]\s*['\x22]?([a-zA-Z0-9_\-\.]{16,})['\x22]?",
            // IPv4 Addresses (Public/Private scrubbing)
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            // Standard Emails
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        ];

        let mut compiled = Vec::with_capacity(raw_patterns.len());
        for p in raw_patterns {
            let re = Regex::new(p).map_err(|_| RedactionError::InvalidRegexCompilation)?;
            compiled.push(re);
        }

        Ok(Self {
            patterns: compiled,
            redaction_mask: mask.to_string(),
        })
    }

    /// Performs zero-allocation in-place redaction where possible, or allocates a new string if modifications occur.
    /// In true production, this operates on `&mut [u8]` bytes to prevent String UTF-8 overhead.
    pub fn redact_telemetry(&self, payload: &str) -> Result<String, RedactionError> {
        if payload.is_empty() {
            return Err(RedactionError::EmptyPayload);
        }

        let mut scrubbed = payload.to_string();

        for regex in &self.patterns {
            scrubbed = regex.replace_all(&scrubbed, &self.redaction_mask).to_string();
        }

        Ok(scrubbed)
    }
}
