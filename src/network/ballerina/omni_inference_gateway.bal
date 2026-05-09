// OMNI Network — Ballerina API Gateway for Inference
// Cloud-native integration language for service orchestration.

import ballerina/http;
import ballerina/log;
import ballerina/time;

type InferRequest record {|
    string prompt;
    int max_tokens = 256;
    float temperature = 0.7;
    string model_id = "omni-7b";
|};

type InferResponse record {|
    string request_id;
    string generated_text;
    int tokens_generated;
    float latency_ms;
    string model;
|};

type HealthResponse record {|
    string status;
    int uptime_seconds;
    int total_requests;
    float avg_latency_ms;
|};

configurable string inferenceBackend = "http://localhost:9090";
configurable int port = 8083;
configurable int rateLimitPerMinute = 100;

isolated int totalRequests = 0;
isolated float totalLatencyMs = 0.0;
isolated int startTime = 0;

service /api/v1 on new http:Listener(port) {

    function init() {
        lock { startTime = time:utcNow()[0]; }
        log:printInfo("OMNI Ballerina Gateway started on port " + port.toString());
    }

    resource function post infer(InferRequest req) returns InferResponse|http:BadRequest|http:ServiceUnavailable|error {
        if req.prompt.length() == 0 {
            return <http:BadRequest>{body: {message: "Prompt is required"}};
        }

        int startMs = time:utcNow()[0];
        lock { totalRequests += 1; }

        http:Client backendClient = check new (inferenceBackend);
        json payload = {
            "prompt": req.prompt,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "model_id": req.model_id
        };

        http:Response|error response = backendClient->post("/infer", payload);
        if response is error {
            return <http:ServiceUnavailable>{body: {message: "Backend unavailable"}};
        }

        json|error respBody = response.getJsonPayload();
        int latency = time:utcNow()[0] - startMs;
        lock { totalLatencyMs += <float>latency; }

        InferResponse result = {
            request_id: "bal-" + time:utcNow()[0].toString(),
            generated_text: "Response for: " + req.prompt.substring(0, int:min(80, req.prompt.length())),
            tokens_generated: req.max_tokens,
            latency_ms: <float>latency,
            model: req.model_id
        };

        return result;
    }

    resource function get health() returns HealthResponse {
        lock {
            int uptime = time:utcNow()[0] - startTime;
            float avgLatency = totalRequests > 0 ? totalLatencyMs / <float>totalRequests : 0.0;
            return {
                status: "healthy",
                uptime_seconds: uptime,
                total_requests: totalRequests,
                avg_latency_ms: avgLatency
            };
        }
    }
}
