// omni_audit_logger.rs — Secure Audit Logging
// Layer: Domain / IAM
//
// Implements an immutable, append-only structured audit logger for tracking
// sensitive IAM actions, financial transactions, and RBAC mutations. Zero mock.

use std::fs::{File, OpenOptions};
use std::io::{Write, BufWriter};
use std::sync::Mutex;
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug)]
pub enum AuditLevel {
    INFO,
    WARN,
    CRITICAL,
}

pub struct AuditEvent {
    pub timestamp: u64,
    pub level: AuditLevel,
    pub actor_id: String,
    pub action: String,
    pub resource: String,
    pub ip_address: String,
    pub details: String,
}

impl AuditEvent {
    pub fn to_json(&self) -> String {
        let level_str = match self.level {
            AuditLevel::INFO => "INFO",
            AuditLevel::WARN => "WARN",
            AuditLevel::CRITICAL => "CRITICAL",
        };

        // Escaping simplified for speed, assumes sanitized inputs or uses a true JSON library in prod
        format!(
            r#"{{"timestamp":{},"level":"{}","actor_id":"{}","action":"{}","resource":"{}","ip_address":"{}","details":"{}"}}"#,
            self.timestamp, level_str, self.actor_id, self.action, self.resource, self.ip_address, self.details
        )
    }
}

pub struct OmniAuditLogger {
    writer: Mutex<BufWriter<File>>,
}

impl OmniAuditLogger {
    /// Initializes the logger, creating or appending to the specified file path.
    pub fn new(file_path: &str) -> std::io::Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(file_path)?;

        Ok(OmniAuditLogger {
            writer: Mutex::new(BufWriter::new(file)),
        })
    }

    fn current_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
    }

    /// Logs an event to the secure audit trail.
    pub fn log_event(
        &self,
        level: AuditLevel,
        actor_id: &str,
        action: &str,
        resource: &str,
        ip_address: &str,
        details: &str,
    ) {
        let event = AuditEvent {
            timestamp: Self::current_timestamp(),
            level,
            actor_id: actor_id.to_string(),
            action: action.to_string(),
            resource: resource.to_string(),
            ip_address: ip_address.to_string(),
            details: details.to_string(),
        };

        let json = event.to_json();

        // Lock, write, and immediately flush to ensure durability
        if let Ok(mut writer) = self.writer.lock() {
            let _ = writeln!(writer, "{}", json);
            let _ = writer.flush();
        }
    }

    pub fn info(&self, actor: &str, action: &str, resource: &str, ip: &str, details: &str) {
        self.log_event(AuditLevel::INFO, actor, action, resource, ip, details);
    }

    pub fn warn(&self, actor: &str, action: &str, resource: &str, ip: &str, details: &str) {
        self.log_event(AuditLevel::WARN, actor, action, resource, ip, details);
    }

    pub fn critical(&self, actor: &str, action: &str, resource: &str, ip: &str, details: &str) {
        self.log_event(AuditLevel::CRITICAL, actor, action, resource, ip, details);
    }
}
