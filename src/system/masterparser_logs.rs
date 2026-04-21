// ===========================================================================
// OMNI SYSTEM LAYER — MASTERPARSER FORENSIC LOG ANALYZER
// ===========================================================================
// Source Paradigm : securityjoes/MasterParser
// Domain Layer   : System (Bare-metal I/O, forensic data extraction)
// Language        : Rust
// Function        : Parses Linux system logs (auth.log, syslog, etc.) to
//                   extract SSH events, user creations, sudo activity,
//                   IP addresses, and failed login attempts for DFIR
// ===========================================================================

use std::collections::HashMap;
use std::fmt;

// ---- Data Types -----------------------------------------------------------

#[derive(Debug, Clone, PartialEq)]
pub enum LogEventType {
    SshLoginSuccess,
    SshLoginFailed,
    SshDisconnect,
    UserCreated,
    UserDeleted,
    SudoCommand,
    ServiceStart,
    ServiceStop,
    CronExecution,
    UnknownEvent,
}

#[derive(Debug, Clone)]
pub struct LogEntry {
    pub timestamp: String,
    pub hostname: String,
    pub process: String,
    pub pid: Option<u32>,
    pub event_type: LogEventType,
    pub message: String,
    pub source_ip: Option<String>,
    pub username: Option<String>,
    pub port: Option<u16>,
}

#[derive(Debug)]
pub struct ForensicReport {
    pub total_entries: usize,
    pub ssh_successes: Vec<LogEntry>,
    pub ssh_failures: Vec<LogEntry>,
    pub user_changes: Vec<LogEntry>,
    pub sudo_events: Vec<LogEntry>,
    pub unique_ips: Vec<String>,
    pub ip_frequency: HashMap<String, u32>,
    pub username_frequency: HashMap<String, u32>,
}

// ---- Core Parser ----------------------------------------------------------

pub struct MasterParserEngine;

impl MasterParserEngine {
    pub fn new() -> Self {
        println!("[MASTERPARSER-OMNI-RS] Initializing forensic log parser engine.");
        MasterParserEngine
    }

    /// Parse a single syslog-format line into a structured LogEntry.
    /// Format: "Mon DD HH:MM:SS hostname process[pid]: message"
    pub fn parse_line(&self, line: &str) -> Option<LogEntry> {
        let parts: Vec<&str> = line.splitn(4, ' ').collect();
        if parts.len() < 4 {
            return None;
        }

        // Extract timestamp (first 3 tokens: "Apr 15 10:23:45")
        let line_parts: Vec<&str> = line.splitn(6, ' ').collect();
        if line_parts.len() < 6 {
            return None;
        }
        let timestamp = format!("{} {} {}", line_parts[0], line_parts[1], line_parts[2]);
        let hostname = line_parts[3].to_string();

        // Parse process[pid]
        let proc_field = line_parts[4].trim_end_matches(':');
        let (process, pid) = if let Some(bracket_pos) = proc_field.find('[') {
            let proc_name = &proc_field[..bracket_pos];
            let pid_str = proc_field[bracket_pos + 1..].trim_end_matches(']');
            (proc_name.to_string(), pid_str.parse::<u32>().ok())
        } else {
            (proc_field.to_string(), None)
        };

        let message = if line_parts.len() > 5 { line_parts[5..].join(" ") } else { String::new() };

        // Classify the event
        let event_type = self.classify_event(&process, &message);
        let source_ip = self.extract_ip(&message);
        let username = self.extract_username(&message);
        let port = self.extract_port(&message);

        Some(LogEntry {
            timestamp, hostname, process, pid,
            event_type, message, source_ip, username, port,
        })
    }

    /// Classify a log message into a forensic event type.
    fn classify_event(&self, process: &str, message: &str) -> LogEventType {
        let msg_lower = message.to_lowercase();
        if process.starts_with("sshd") {
            if msg_lower.contains("accepted") {
                return LogEventType::SshLoginSuccess;
            }
            if msg_lower.contains("failed password") || msg_lower.contains("invalid user") {
                return LogEventType::SshLoginFailed;
            }
            if msg_lower.contains("disconnected") || msg_lower.contains("connection closed") {
                return LogEventType::SshDisconnect;
            }
        }
        if process.starts_with("useradd") || msg_lower.contains("new user") {
            return LogEventType::UserCreated;
        }
        if process.starts_with("userdel") {
            return LogEventType::UserDeleted;
        }
        if process.starts_with("sudo") || msg_lower.contains("command=") {
            return LogEventType::SudoCommand;
        }
        if msg_lower.contains("started") && process.starts_with("systemd") {
            return LogEventType::ServiceStart;
        }
        if msg_lower.contains("stopped") && process.starts_with("systemd") {
            return LogEventType::ServiceStop;
        }
        if process.starts_with("cron") || process.starts_with("CRON") {
            return LogEventType::CronExecution;
        }
        LogEventType::UnknownEvent
    }

    /// Extract IPv4 addresses from a log message using manual scanning.
    fn extract_ip(&self, message: &str) -> Option<String> {
        // Look for "from X.X.X.X" pattern
        if let Some(pos) = message.find("from ") {
            let after = &message[pos + 5..];
            let ip_candidate: String = after.chars()
                .take_while(|c| c.is_ascii_digit() || *c == '.')
                .collect();
            if ip_candidate.matches('.').count() == 3 && ip_candidate.len() >= 7 {
                return Some(ip_candidate);
            }
        }
        None
    }

    /// Extract username from common log patterns.
    fn extract_username(&self, message: &str) -> Option<String> {
        // "for <user> from" or "user <user>"
        for prefix in &["for ", "user "] {
            if let Some(pos) = message.find(prefix) {
                let after = &message[pos + prefix.len()..];
                let name: String = after.chars()
                    .take_while(|c| c.is_alphanumeric() || *c == '_' || *c == '-' || *c == '.')
                    .collect();
                if !name.is_empty() {
                    return Some(name);
                }
            }
        }
        None
    }

    /// Extract port number from "port XXXXX" pattern.
    fn extract_port(&self, message: &str) -> Option<u16> {
        if let Some(pos) = message.find("port ") {
            let after = &message[pos + 5..];
            let port_str: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
            return port_str.parse::<u16>().ok();
        }
        None
    }

    /// Analyze a full log buffer and produce a forensic report.
    pub fn analyze(&self, log_contents: &str) -> ForensicReport {
        println!("[MASTERPARSER-OMNI-RS] Analyzing log buffer ({} bytes)...", log_contents.len());

        let mut report = ForensicReport {
            total_entries: 0,
            ssh_successes: Vec::new(),
            ssh_failures: Vec::new(),
            user_changes: Vec::new(),
            sudo_events: Vec::new(),
            unique_ips: Vec::new(),
            ip_frequency: HashMap::new(),
            username_frequency: HashMap::new(),
        };

        for line in log_contents.lines() {
            if let Some(entry) = self.parse_line(line) {
                report.total_entries += 1;

                // Track IP frequency
                if let Some(ref ip) = entry.source_ip {
                    *report.ip_frequency.entry(ip.clone()).or_insert(0) += 1;
                }
                // Track username frequency
                if let Some(ref user) = entry.username {
                    *report.username_frequency.entry(user.clone()).or_insert(0) += 1;
                }

                match entry.event_type {
                    LogEventType::SshLoginSuccess => report.ssh_successes.push(entry),
                    LogEventType::SshLoginFailed => report.ssh_failures.push(entry),
                    LogEventType::UserCreated | LogEventType::UserDeleted => {
                        report.user_changes.push(entry)
                    }
                    LogEventType::SudoCommand => report.sudo_events.push(entry),
                    _ => {}
                }
            }
        }

        report.unique_ips = report.ip_frequency.keys().cloned().collect();

        println!("[MASTERPARSER-OMNI-RS] Analysis complete:");
        println!("  Total entries parsed : {}", report.total_entries);
        println!("  SSH successes        : {}", report.ssh_successes.len());
        println!("  SSH failures         : {}", report.ssh_failures.len());
        println!("  User changes         : {}", report.user_changes.len());
        println!("  Sudo events          : {}", report.sudo_events.len());
        println!("  Unique IPs           : {}", report.unique_ips.len());

        report
    }
}

// fn main() {
//     let parser = MasterParserEngine::new();
//     let sample = r#"Apr 15 10:23:45 webserver sshd[12345]: Accepted publickey for admin from 192.168.1.100 port 54321 ssh2
// Apr 15 10:24:01 webserver sshd[12346]: Failed password for invalid user test from 10.0.0.5 port 22334 ssh2
// Apr 15 10:25:00 webserver sudo[12400]: admin : TTY=pts/0 ; PWD=/root ; USER=root ; COMMAND=/bin/cat /etc/shadow
// Apr 15 10:26:00 webserver useradd[12500]: new user: name=backdoor, UID=1001, GID=1001
// "#;
//     let report = parser.analyze(sample);
// }
