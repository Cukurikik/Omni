<?php
// OMNI Framework - PHP Legacy Bridge for AI Pipelines
// Bridges legacy CMS systems to modern OMNI LLM Pipelines

class OmniPipelineBridge {
    private $apiEndpoint = "http://omni-python-compute:8080/api/pipeline/execute";

    public function dispatchTextForProcessing(string $textData): array {
        $payload = json_encode(["text" => $textData, "pipeline" => "default_llm_pipeline"]);
        
        // Use cURL for fast legacy integration
        $ch = curl_init($this->apiEndpoint);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        if (!$response) {
            return ["status" => "error", "message" => "OMNI Compute node unreachable"];
        }
        
        return json_decode($response, true);
    }
}
?>
