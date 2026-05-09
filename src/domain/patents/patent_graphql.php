<?php
//=============================================================================
// OMNI DOMAIN LAYER — LEGACY PHP GRAPHQL BRIDGE (PHP)
// BATCH: 31 | SEMESTER: 16
// DESCRIPTION: Bridges legacy PHP architectures (e.g. older CMS) into the 
//              OMNI GraphQL API for Patent search interactions.
//=============================================================================

namespace Omni\Domain\Patents;

use Exception;

/**
 * OMNI IDIOM: php::web legacy integration
 * Provides a clean interface for a legacy PHP application to consume the modern
 * Omni AI-powered patent classification system.
 */
class PatentBridge {
    private string $omniRpcSocket;

    public function __construct(string $omniRpcSocket = "unix:///tmp/omni_rpc.sock") {
        $this->omniRpcSocket = $omniRpcSocket;
    }

    public function searchPatents(string $query, int $topK = 5): array {
        $payload = [
            'method' => 'domain.patents.search',
            'params' => [
                'query_text' => $query,
                'top_k' => $topK
            ]
        ];

        // Send over UNIX socket to OMNI Go/Rust core router
        $result = $this->sendToOmni($payload);

        if (isset($result['error'])) {
            throw new Exception("OMNI Core Error: " . $result['error']);
        }

        return $result['data'] ?? [];
    }

    private function sendToOmni(array $payload): array {
        // Zero-mock socket interaction
        $fp = stream_socket_client($this->omniRpcSocket, $errno, $errstr, 3);
        if (!$fp) {
            throw new Exception("Unable to connect to OMNI Core: $errstr ($errno)");
        }
        
        fwrite($fp, json_encode($payload) . "\n");
        $response = fgets($fp);
        fclose($fp);
        
        return json_decode($response, true) ?? [];
    }
}
