/// Omni Mother System - Security Layer
/// HTTP Strict Transport Security (HSTS) Header Enforcer middleware

pub struct HstsEnforcer {
    max_age_seconds: u64,
    include_subdomains: bool,
    preload: bool,
}

impl HstsEnforcer {
    pub fn new() -> Self {
        Self {
            max_age_seconds: 31536000, // 1 year
            include_subdomains: true,
            preload: true,
        }
    }

    /// Generates the strict HSTS header string
    pub fn get_header_value(&self) -> String {
        let mut header = format!("max-age={}", self.max_age_seconds);
        
        if self.include_subdomains {
            header.push_str("; includeSubDomains");
        }
        
        if self.preload {
            header.push_str("; preload");
        }
        
        header
    }

    /// Validates if an incoming request is secure (HTTPS)
    /// In Omni, SSL termination might happen at load balancers, so we strictly check
    /// forward headers if the direct protocol is not HTTPS.
    pub fn is_secure_request(&self, is_tls: bool, x_forwarded_proto: Option<&str>) -> bool {
        if is_tls {
            return true;
        }

        if let Some(proto) = x_forwarded_proto {
            if proto.eq_ignore_ascii_case("https") {
                return true;
            }
        }

        false
    }
}

// Example usage mapping to Omni's HTTP pipeline:
/*
    let hsts = HstsEnforcer::new();
    if hsts.is_secure_request(conn.is_tls(), headers.get("x-forwarded-proto")) {
        response.headers.insert("Strict-Transport-Security", hsts.get_header_value());
    } else {
        // Return 301 Permanent Redirect to HTTPS
    }
*/
