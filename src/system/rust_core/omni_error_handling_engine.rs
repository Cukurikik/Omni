// ===========================================================================
// OMNI ERROR HANDLING ENGINE (SEMESTER 3 — BATCH 38.9)
// ===========================================================================
// Absorbed From  : thiserror + anyhow + miette + color-eyre + snafu
// Logic Inherited: Rust / System Layer (Error Architecture & Diagnostics)
// ===========================================================================
//
// By studying thiserror and anyhow, Mother learned Rust error patterns:
//   1. Custom error types via enum implement std::error::Error
//   2. thiserror derives Display and Error boilerplate
//   3. anyhow::Error erases types for application-level error handling
//   4. Error chains: source() links cause of error (wrapping)
//   5. miette adds rich diagnostics: labels, snippets, help text

use std::collections::HashMap;
use std::fmt;

// ============================================================
// PART 1: Error Type Builder (thiserror-inspired)
// ============================================================

/// Severity levels for errors.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Severity {
    Warning,
    Error,
    Critical,
    Fatal,
}

impl fmt::Display for Severity {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Severity::Warning => write!(f, "WARNING"),
            Severity::Error => write!(f, "ERROR"),
            Severity::Critical => write!(f, "CRITICAL"),
            Severity::Fatal => write!(f, "FATAL"),
        }
    }
}

/// SourceLocation captures where an error originated.
#[derive(Debug, Clone)]
pub struct SourceLocation {
    pub file: &'static str,
    pub line: u32,
    pub column: u32,
}

impl fmt::Display for SourceLocation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:{}:{}", self.file, self.line, self.column)
    }
}

/// Macro-like helper to capture source location.
#[macro_export]
macro_rules! here {
    () => {
        SourceLocation {
            file: file!(),
            line: line!(),
            column: column!(),
        }
    };
}

/// OmniError: rich error type with code, context chain, and diagnostics.
#[derive(Debug)]
pub struct OmniError {
    code: String,
    message: String,
    severity: Severity,
    source: Option<Box<dyn std::error::Error + Send + Sync>>,
    context: Vec<String>,
    help: Option<String>,
    location: Option<SourceLocation>,
    metadata: HashMap<String, String>,
}

impl OmniError {
    /// Create a new error with code and message.
    pub fn new(code: impl Into<String>, message: impl Into<String>) -> Self {
        Self {
            code: code.into(),
            message: message.into(),
            severity: Severity::Error,
            source: None,
            context: Vec::new(),
            help: None,
            location: None,
            metadata: HashMap::new(),
        }
    }

    /// Set severity.
    pub fn severity(mut self, severity: Severity) -> Self {
        self.severity = severity;
        self
    }

    /// Wrap an underlying error as the source.
    pub fn caused_by<E: std::error::Error + Send + Sync + 'static>(mut self, source: E) -> Self {
        self.source = Some(Box::new(source));
        self
    }

    /// Add contextual information (builds error chain).
    pub fn context(mut self, ctx: impl Into<String>) -> Self {
        self.context.push(ctx.into());
        self
    }

    /// Add a help/suggestion message.
    pub fn help(mut self, help: impl Into<String>) -> Self {
        self.help = Some(help.into());
        self
    }

    /// Set the source location.
    pub fn at(mut self, location: SourceLocation) -> Self {
        self.location = Some(location);
        self
    }

    /// Add arbitrary metadata.
    pub fn meta(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.metadata.insert(key.into(), value.into());
        self
    }

    /// Get the error code.
    pub fn code(&self) -> &str {
        &self.code
    }

    /// Check if this is a specific error code.
    pub fn is_code(&self, code: &str) -> bool {
        self.code == code
    }

    /// Rich diagnostic report.
    pub fn report(&self) -> String {
        let mut report = String::new();

        report.push_str(&format!("[{}] {}: {}\n", self.severity, self.code, self.message));

        if let Some(loc) = &self.location {
            report.push_str(&format!("  --> {}\n", loc));
        }

        for (i, ctx) in self.context.iter().enumerate() {
            report.push_str(&format!("  {}. {}\n", i + 1, ctx));
        }

        if let Some(source) = &self.source {
            report.push_str(&format!("  caused by: {}\n", source));
            // Walk the error chain
            let mut current: &dyn std::error::Error = source.as_ref();
            while let Some(next) = current.source() {
                report.push_str(&format!("  caused by: {}\n", next));
                current = next;
            }
        }

        if !self.metadata.is_empty() {
            report.push_str("  metadata:\n");
            for (k, v) in &self.metadata {
                report.push_str(&format!("    {}: {}\n", k, v));
            }
        }

        if let Some(help) = &self.help {
            report.push_str(&format!("  help: {}\n", help));
        }

        report
    }
}

impl fmt::Display for OmniError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{}] {}: {}", self.severity, self.code, self.message)
    }
}

impl std::error::Error for OmniError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        self.source.as_ref().map(|e| e.as_ref() as &(dyn std::error::Error + 'static))
    }
}

// ============================================================
// PART 2: Result Extension Methods
// ============================================================

/// Extension trait for Result to add context and error mapping.
pub trait ResultExt<T, E> {
    /// Add context to an error.
    fn context(self, ctx: impl Into<String>) -> Result<T, OmniError>
    where
        E: std::error::Error + Send + Sync + 'static;

    /// Add context lazily (only on error).
    fn with_context<F: FnOnce() -> String>(self, f: F) -> Result<T, OmniError>
    where
        E: std::error::Error + Send + Sync + 'static;
}

impl<T, E> ResultExt<T, E> for Result<T, E> {
    fn context(self, ctx: impl Into<String>) -> Result<T, OmniError>
    where
        E: std::error::Error + Send + Sync + 'static,
    {
        self.map_err(|e| {
            OmniError::new("CONTEXT", ctx.into()).caused_by(e)
        })
    }

    fn with_context<F: FnOnce() -> String>(self, f: F) -> Result<T, OmniError>
    where
        E: std::error::Error + Send + Sync + 'static,
    {
        self.map_err(|e| {
            OmniError::new("CONTEXT", f()).caused_by(e)
        })
    }
}

/// Extension trait for Option to convert to Result with error.
pub trait OptionExt<T> {
    /// Convert None to an OmniError.
    fn ok_or_omni(self, code: &str, message: &str) -> Result<T, OmniError>;
}

impl<T> OptionExt<T> for Option<T> {
    fn ok_or_omni(self, code: &str, message: &str) -> Result<T, OmniError> {
        self.ok_or_else(|| OmniError::new(code, message))
    }
}

// ============================================================
// PART 3: Error Registry (Catalog)
// ============================================================

/// ErrorCatalog: defines known error codes with descriptions.
pub struct ErrorCatalog {
    entries: HashMap<String, ErrorDefinition>,
}

#[derive(Debug, Clone)]
pub struct ErrorDefinition {
    pub code: String,
    pub message_template: String,
    pub severity: Severity,
    pub help: Option<String>,
}

impl ErrorCatalog {
    pub fn new() -> Self {
        Self {
            entries: HashMap::new(),
        }
    }

    /// Register an error definition.
    pub fn define(
        &mut self,
        code: impl Into<String>,
        message_template: impl Into<String>,
        severity: Severity,
        help: Option<String>,
    ) {
        let code = code.into();
        self.entries.insert(code.clone(), ErrorDefinition {
            code,
            message_template: message_template.into(),
            severity,
            help,
        });
    }

    /// Create an error from a catalog entry.
    pub fn create(&self, code: &str) -> Option<OmniError> {
        self.entries.get(code).map(|def| {
            let mut err = OmniError::new(&def.code, &def.message_template)
                .severity(def.severity);
            if let Some(help) = &def.help {
                err = err.help(help.clone());
            }
            err
        })
    }

    /// Check if a code is defined.
    pub fn has(&self, code: &str) -> bool {
        self.entries.contains_key(code)
    }

    /// Get all registered error codes.
    pub fn codes(&self) -> Vec<&str> {
        self.entries.keys().map(|s| s.as_str()).collect()
    }
}

// ============================================================
// PART 4: Panic Handler
// ============================================================

/// Install a custom panic hook that formats panics as OmniError reports.
pub fn install_panic_handler() {
    std::panic::set_hook(Box::new(|info| {
        let location = info.location().map(|l| {
            format!("{}:{}:{}", l.file(), l.line(), l.column())
        }).unwrap_or_else(|| "unknown".to_string());

        let message = if let Some(s) = info.payload().downcast_ref::<&str>() {
            s.to_string()
        } else if let Some(s) = info.payload().downcast_ref::<String>() {
            s.clone()
        } else {
            "unknown panic".to_string()
        };

        eprintln!("╔══════════════════════════════════════╗");
        eprintln!("║        OMNI PANIC REPORT             ║");
        eprintln!("╠══════════════════════════════════════╣");
        eprintln!("║ Location: {}", location);
        eprintln!("║ Message:  {}", message);
        eprintln!("╚══════════════════════════════════════╝");
    }));
}

// ============================================================
// Diagnostics
// ============================================================

pub fn diagnostics() -> HashMap<&'static str, Vec<&'static str>> {
    let mut m = HashMap::new();
    m.insert("engine", vec!["OmniErrorHandlingEngine"]);
    m.insert("layer", vec!["Rust System"]);
    m.insert("components", vec![
        "OmniError", "ResultExt", "OptionExt",
        "ErrorCatalog", "PanicHandler", "SourceLocation",
    ]);
    m.insert("learned_logic", vec![
        "thiserror-derive-display-error",
        "anyhow-type-erased-context",
        "error-chain-source-walk",
        "miette-rich-diagnostics",
        "result-ext-context-lazy",
        "error-catalog-code-registry",
        "severity-warning-error-critical",
        "panic-hook-formatted-report",
    ]);
    m
}
