<?php
/**
 * OMNI Legacy Bridge
 * Exposes a REST endpoint for older PHP/CMS architectures to trigger OMNI LLM tasks.
 */
header('Content-Type: application/json');

function handleOmniRequest() {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!isset($input['prompt'])) {
        http_response_code(400);
        echo json_encode(["error" => "Missing 'prompt' in request body"]);
        return;
    }

    $prompt = $input['prompt'];
    
    // Simulate sending via cURL to OMNI Rust Kernel
    $omni_response = "Generated response from OMNI for: " . substr($prompt, 0, 50);

    echo json_encode([
        "status" => "success",
        "omni_latency_ms" => 14,
        "response" => $omni_response
    ]);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    handleOmniRequest();
} else {
    http_response_code(405);
    echo json_encode(["error" => "Method not allowed"]);
}
