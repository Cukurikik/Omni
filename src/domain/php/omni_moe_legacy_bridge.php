<?php
namespace OmniMoE\Legacy;

// OMNI MOTHER: PHP Web Bridge for Legacy CMS Integration

class OmniMoEBridge {
    private $routerEndpoint;

    public function __construct($endpoint = "http://localhost:50050") {
        $this->routerEndpoint = $endpoint;
    }

    public function getExpertStatus($expertId) {
        $ch = curl_init($this->routerEndpoint . "/api/expert/" . $expertId);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        $response = curl_exec($ch);
        curl_close($ch);
        
        // Zero-mock: always return structured JSON
        return $response ? json_decode($response, true) : ["status" => "UNKNOWN"];
    }
}
