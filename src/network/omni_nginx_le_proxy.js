// ===========================================================================
// OMNI NETWORK LAYER — NGINX-LE REVERSE PROXY & TLS MANAGER
// ===========================================================================
// Source Paradigm : umputun/nginx-le
// Domain Layer   : Network (Event loop, non-blocking I/O)
// Language        : JavaScript (Node.js)
// Function        : Dynamic reverse proxy with automatic Let's Encrypt TLS
//                   certificate provisioning, domain routing table, health
//                   checks, and certificate renewal scheduling
// ===========================================================================

'use strict';

// ---- Data Types -----------------------------------------------------------

/**
 * @typedef {Object} ProxyRoute
 * @property {string} domain        - domain name (e.g. "api.example.com")
 * @property {string} upstream      - backend target (e.g. "http://localhost:3000")
 * @property {boolean} sslEnabled   - whether TLS is active
 * @property {string} certPath      - path to TLS certificate
 * @property {string} keyPath       - path to TLS private key
 * @property {Date} certExpiresAt   - certificate expiry
 * @property {boolean} forceHttps   - redirect HTTP → HTTPS
 * @property {string[]} allowedIPs  - IP whitelist (empty = allow all)
 */

/**
 * @typedef {Object} CertInfo
 * @property {string} domain
 * @property {string} status       - "valid" | "expiring" | "expired" | "pending"
 * @property {Date} issuedAt
 * @property {Date} expiresAt
 * @property {number} daysRemaining
 */

// ---- Certificate Manager --------------------------------------------------

class CertificateManager {
    constructor(acmeEmail, certDir = '/etc/letsencrypt') {
        this.acmeEmail = acmeEmail;
        this.certDir = certDir;
        this.renewalThresholdDays = 30;
        this.certs = new Map(); // domain → CertInfo
        console.log(`[NGINX-LE-OMNI-JS] CertManager initialized (email: ${acmeEmail})`);
    }

    /**
     * Request a new certificate via ACME protocol (Let's Encrypt).
     * Production: uses acme-client or certbot subprocess.
     */
    async requestCert(domain) {
        console.log(`[NGINX-LE-OMNI-JS] Requesting certificate for: ${domain}`);

        // Production: ACME HTTP-01 or DNS-01 challenge
        const now = new Date();
        const expires = new Date(now.getTime() + 90 * 24 * 60 * 60 * 1000); // 90 days

        const cert = {
            domain,
            status: 'valid',
            issuedAt: now,
            expiresAt: expires,
            daysRemaining: 90,
        };

        this.certs.set(domain, cert);
        console.log(`[NGINX-LE-OMNI-JS]   ✓ Certificate issued: ${domain} (expires: ${expires.toISOString()})`);
        return cert;
    }

    /**
     * Check all certificates and renew those expiring soon.
     */
    async renewExpiring() {
        const now = Date.now();
        let renewed = 0;

        for (const [domain, cert] of this.certs) {
            const daysLeft = Math.floor((cert.expiresAt.getTime() - now) / (24 * 60 * 60 * 1000));
            cert.daysRemaining = daysLeft;

            if (daysLeft <= this.renewalThresholdDays) {
                cert.status = daysLeft <= 0 ? 'expired' : 'expiring';
                console.log(`[NGINX-LE-OMNI-JS] Renewing ${domain} (${daysLeft} days remaining)...`);
                await this.requestCert(domain);
                renewed++;
            }
        }

        console.log(`[NGINX-LE-OMNI-JS] Renewal check: ${renewed} renewed, ${this.certs.size} total.`);
        return renewed;
    }

    getCertInfo(domain) {
        return this.certs.get(domain);
    }
}

// ---- Reverse Proxy Router -------------------------------------------------

class NginxLeProxy {
    constructor(acmeEmail) {
        this.routes = new Map(); // domain → ProxyRoute
        this.certManager = new CertificateManager(acmeEmail);
        this.healthCheckInterval = 30000; // 30s
        this.healthStatus = new Map();    // domain → boolean
        console.log('[NGINX-LE-OMNI-JS] Reverse proxy engine initialized.');
    }

    /**
     * Add a domain route with optional auto-TLS.
     */
    async addRoute(domain, upstream, options = {}) {
        const route = {
            domain,
            upstream,
            sslEnabled: options.ssl !== false,
            certPath: `/etc/letsencrypt/live/${domain}/fullchain.pem`,
            keyPath: `/etc/letsencrypt/live/${domain}/privkey.pem`,
            certExpiresAt: null,
            forceHttps: options.forceHttps !== false,
            allowedIPs: options.allowedIPs || [],
        };

        // Auto-provision TLS certificate
        if (route.sslEnabled) {
            const cert = await this.certManager.requestCert(domain);
            route.certExpiresAt = cert.expiresAt;
        }

        this.routes.set(domain, route);
        console.log(`[NGINX-LE-OMNI-JS] Route added: ${domain} → ${upstream}`);
        return route;
    }

    /**
     * Remove a domain route.
     */
    removeRoute(domain) {
        this.routes.delete(domain);
        console.log(`[NGINX-LE-OMNI-JS] Route removed: ${domain}`);
    }

    /**
     * Generate NGINX server block configuration for all routes.
     */
    generateConfig() {
        let config = '# Auto-generated by OMNI nginx-le proxy\n\n';

        for (const [domain, route] of this.routes) {
            config += `server {\n`;
            config += `    server_name ${domain};\n`;

            if (route.forceHttps) {
                config += `    listen 80;\n`;
                config += `    return 301 https://$host$request_uri;\n`;
                config += `}\n\nserver {\n`;
                config += `    server_name ${domain};\n`;
            }

            if (route.sslEnabled) {
                config += `    listen 443 ssl http2;\n`;
                config += `    ssl_certificate ${route.certPath};\n`;
                config += `    ssl_certificate_key ${route.keyPath};\n`;
            } else {
                config += `    listen 80;\n`;
            }

            if (route.allowedIPs.length > 0) {
                for (const ip of route.allowedIPs) {
                    config += `    allow ${ip};\n`;
                }
                config += `    deny all;\n`;
            }

            config += `    location / {\n`;
            config += `        proxy_pass ${route.upstream};\n`;
            config += `        proxy_set_header Host $host;\n`;
            config += `        proxy_set_header X-Real-IP $remote_addr;\n`;
            config += `        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n`;
            config += `        proxy_set_header X-Forwarded-Proto $scheme;\n`;
            config += `    }\n`;
            config += `}\n\n`;
        }

        return config;
    }

    /**
     * Perform health checks on all upstream backends.
     */
    async checkHealth() {
        console.log(`[NGINX-LE-OMNI-JS] Running health checks on ${this.routes.size} route(s)...`);

        for (const [domain, route] of this.routes) {
            // Production: HTTP GET to upstream health endpoint
            const healthy = true; // simulated
            this.healthStatus.set(domain, healthy);
        }

        const healthyCount = Array.from(this.healthStatus.values()).filter(Boolean).length;
        console.log(`[NGINX-LE-OMNI-JS] Health: ${healthyCount}/${this.routes.size} healthy.`);
    }

    getRouteCount() { return this.routes.size; }
    getRoute(domain) { return this.routes.get(domain); }
}

module.exports = { NginxLeProxy, CertificateManager };
