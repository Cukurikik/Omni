<?php

declare(strict_types=1);

namespace Omni\Security\Web;

/**
 * Omni Mother System - Security Layer
 * Generates strict Content-Security-Policy (CSP) headers to prevent XSS.
 */
final class CspGenerator {
    private string $nonce;

    public function __construct() {
        // Cryptographically secure nonce generation for inline scripts/styles
        try {
            $this->nonce = base64_encode(random_bytes(16));
        } catch (\Exception $e) {
            // Fallback securely if CSPRNG is somehow broken
            $this->nonce = base64_encode(hash('sha256', uniqid((string)mt_rand(), true), true));
        }
    }

    public function getNonce(): string {
        return $this->nonce;
    }

    /**
     * Compiles the strict CSP level 3 header string.
     * Enforces default-src 'none' to ensure explicit whitelisting.
     */
    public function generateHeaderString(): string {
        $directives = [
            "default-src" => ["'none'"],
            
            // Allow scripts only with the cryptographic nonce
            "script-src" => [
                "'strict-dynamic'",
                "'nonce-" . $this->nonce . "'",
                // Fallback for older browsers
                "'unsafe-inline'", 
                "https:"
            ],
            
            // Styles
            "style-src" => [
                "'nonce-" . $this->nonce . "'",
                // Sometimes external stylesheets need whitelisting here
            ],
            
            // Images
            "img-src" => [
                "'self'",
                "data:", // Base64 images
                "https://cdn.omni-framework.dev"
            ],
            
            // Fonts
            "font-src" => [
                "'self'",
                "https://fonts.gstatic.com"
            ],
            
            // Connect (Fetch/XHR/WebSockets)
            "connect-src" => [
                "'self'",
                "wss://api.omni-framework.dev",
                "https://api.omni-framework.dev"
            ],
            
            // Strict frame protection against clickjacking
            "frame-ancestors" => ["'none'"],
            "base-uri" => ["'none'"],
            "form-action" => ["'self'"],
            
            // Upgrade insecure requests automatically
            "upgrade-insecure-requests" => []
        ];

        $compiled = [];
        foreach ($directives as $directive => $sources) {
            if (empty($sources)) {
                $compiled[] = $directive;
            } else {
                $compiled[] = $directive . " " . implode(" ", $sources);
            }
        }

        return implode("; ", $compiled);
    }
}
