<?php
// moe_php_legacy_bridge.php — Domain / CMS
// Layer: Domain / Web — Legacy CMS Bridge
//
// The OMNI framework is modern, but it must interface with legacy enterprise systems.
// This PHP script acts as a sidecar bridge, allowing older WordPress/Drupal sites
// to query the MoE for content generation via a simple HTTP POST, bypassing
// the need for complex gRPC clients in the legacy stack.

namespace Omni\MoE\Bridge;

class LegacyCMSBridge {
    private string $moeEndpoint;

    public function __construct(string $moeEndpoint = "http://localhost:8080/v1/completions") {
        $this->moeEndpoint = $moeEndpoint;
        error_log("[PHP Bridge] Initialized Legacy CMS Bridge to OMNI MoE.");
    }

    /**
     * Sends a request to the MoE to generate an SEO-optimized blog post.
     * 
     * @param string $topic The subject of the article.
     * @param string $tone "professional", "casual", etc.
     * @return string The generated HTML content.
     */
    public function generateArticle(string $topic, string $tone): string {
        $prompt = "[SYSTEM: Act as Expert #7 - Copywriting] Write a {$tone} article about {$topic}. Output HTML.";

        $payload = json_encode([
            "prompt" => $prompt,
            "max_tokens" => 1024,
            "temperature" => 0.7
        ]);

        $ch = curl_init($this->moeEndpoint);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'X-Omni-Caller: PHP-Legacy-Bridge'
        ]);

        $response = curl_exec($ch);
        
        if (curl_errno($ch)) {
            error_log("[PHP Bridge] MoE Connection Error: " . curl_error($ch));
            return "<p>Error connecting to the AI brain.</p>";
        }

        curl_close($ch);

        // Parse OMNI response format
        $data = json_decode($response, true);
        return $data['choices'][0]['text'] ?? "<p>Generation failed.</p>";
    }
}
// Usage:
// $bridge = new LegacyCMSBridge();
// echo $bridge->generateArticle("The future of MoE architectures", "professional");
?>
