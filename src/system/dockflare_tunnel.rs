// ===========================================================================
// OMNI SYSTEM LAYER — DOCKFLARE CLOUDFLARE TUNNEL ENGINE
// ===========================================================================
// Source Paradigm : nicehash/dockflare
// Domain Layer   : System (Memory-safe concurrency, zero-cost abstraction)
// Language        : Rust
// Function        : Manages Cloudflare Tunnel (Argo) connections for secure
//                   ingress routing, automatic DNS record management,
//                   tunnel health monitoring, and multi-service multiplexing
// ===========================================================================

use std::collections::HashMap;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use std::fmt;

// ---- Types ----------------------------------------------------------------

#[derive(Debug, Clone, PartialEq)]
pub enum TunnelProtocol {
    Http,
    Https,
    Tcp,
    Ssh,
    Rdp,
}

impl fmt::Display for TunnelProtocol {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            TunnelProtocol::Http => write!(f, "http"),
            TunnelProtocol::Https => write!(f, "https"),
            TunnelProtocol::Tcp => write!(f, "tcp"),
            TunnelProtocol::Ssh => write!(f, "ssh"),
            TunnelProtocol::Rdp => write!(f, "rdp"),
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum TunnelState {
    Creating,
    Active,
    Degraded,
    Reconnecting,
    Down,
}

// ---- Config Models --------------------------------------------------------

#[derive(Debug, Clone)]
pub struct IngressRule {
    pub hostname: String,
    pub service: String,              // e.g. "http://localhost:3000"
    pub protocol: TunnelProtocol,
    pub path: Option<String>,         // optional path prefix
    pub tls_verify: bool,
    pub connect_timeout_ms: u64,
    pub no_chunked_encoding: bool,
}

impl IngressRule {
    pub fn new(hostname: &str, service: &str, protocol: TunnelProtocol) -> Self {
        IngressRule {
            hostname: hostname.to_string(),
            service: service.to_string(),
            protocol,
            path: None,
            tls_verify: true,
            connect_timeout_ms: 10_000,
            no_chunked_encoding: false,
        }
    }

    /// Generate cloudflared YAML config fragment for this rule.
    pub fn to_config_yaml(&self) -> String {
        let mut yaml = format!(
            "  - hostname: {}\n    service: {}\n",
            self.hostname, self.service
        );
        if let Some(ref path) = self.path {
            yaml.push_str(&format!("    path: {}\n", path));
        }
        if !self.tls_verify {
            yaml.push_str("    originRequest:\n      noTLSVerify: true\n");
        }
        yaml
    }
}

#[derive(Debug, Clone)]
pub struct TunnelConfig {
    pub tunnel_id: String,
    pub tunnel_name: String,
    pub account_id: String,
    pub credentials_file: String,
    pub ingress_rules: Vec<IngressRule>,
    pub metrics_port: u16,
    pub retries: u32,
    pub grace_period_seconds: u64,
}

// ---- DNS Record Manager ---------------------------------------------------

#[derive(Debug, Clone)]
pub struct DnsRecord {
    pub record_type: String,  // "CNAME"
    pub name: String,         // subdomain
    pub content: String,      // tunnel UUID.cfargotunnel.com
    pub proxied: bool,
    pub ttl: u32,
}

pub struct DnsManager {
    records: HashMap<String, DnsRecord>,
    zone_id: String,
}

impl DnsManager {
    pub fn new(zone_id: &str) -> Self {
        println!("[DOCKFLARE-OMNI-RS] DNS manager initialized (zone: {})", zone_id);
        DnsManager {
            records: HashMap::new(),
            zone_id: zone_id.to_string(),
        }
    }

    /// Create or update a DNS CNAME pointing to the tunnel.
    pub fn upsert_record(&mut self, hostname: &str, tunnel_id: &str) -> DnsRecord {
        let record = DnsRecord {
            record_type: "CNAME".to_string(),
            name: hostname.to_string(),
            content: format!("{}.cfargotunnel.com", tunnel_id),
            proxied: true,
            ttl: 1, // auto
        };
        println!(
            "[DOCKFLARE-OMNI-RS] DNS upsert: {} → {}",
            hostname, record.content
        );
        // Production: PUT /zones/{zone_id}/dns_records
        self.records.insert(hostname.to_string(), record.clone());
        record
    }

    pub fn remove_record(&mut self, hostname: &str) -> bool {
        let removed = self.records.remove(hostname).is_some();
        if removed {
            println!("[DOCKFLARE-OMNI-RS] DNS removed: {}", hostname);
        }
        removed
    }

    pub fn list_records(&self) -> Vec<&DnsRecord> {
        self.records.values().collect()
    }
}

// ---- Tunnel Health Monitor ------------------------------------------------

#[derive(Debug)]
pub struct HealthStatus {
    pub tunnel_id: String,
    pub state: TunnelState,
    pub connections: u32,
    pub uptime_seconds: u64,
    pub last_check: u64, // unix timestamp
    pub errors: Vec<String>,
}

pub fn check_tunnel_health(config: &TunnelConfig) -> HealthStatus {
    // Production: GET http://localhost:{metrics_port}/ready
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or(Duration::ZERO)
        .as_secs();

    println!(
        "[DOCKFLARE-OMNI-RS] Health check: {} ({} ingress rules)",
        config.tunnel_name,
        config.ingress_rules.len()
    );

    HealthStatus {
        tunnel_id: config.tunnel_id.clone(),
        state: TunnelState::Active,
        connections: config.ingress_rules.len() as u32,
        uptime_seconds: 0,
        last_check: now,
        errors: Vec::new(),
    }
}

// ---- Tunnel Config Generator ----------------------------------------------

pub fn generate_cloudflared_config(config: &TunnelConfig) -> String {
    let mut yaml = String::new();
    yaml.push_str(&format!("tunnel: {}\n", config.tunnel_id));
    yaml.push_str(&format!("credentials-file: {}\n", config.credentials_file));
    yaml.push_str(&format!("metrics: 0.0.0.0:{}\n", config.metrics_port));
    yaml.push_str(&format!("retries: {}\n", config.retries));
    yaml.push_str(&format!(
        "grace-period: {}s\n",
        config.grace_period_seconds
    ));
    yaml.push_str("\ningress:\n");

    for rule in &config.ingress_rules {
        yaml.push_str(&rule.to_config_yaml());
    }

    // Catch-all rule (required by cloudflared)
    yaml.push_str("  - service: http_status:404\n");

    println!(
        "[DOCKFLARE-OMNI-RS] Generated cloudflared config ({} rules + catch-all)",
        config.ingress_rules.len()
    );
    yaml
}
