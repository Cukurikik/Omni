// OMNI Concurrency Layer — Ballerina AI Inference Service
// Cloud-native inference API with built-in observability.

import ballerina/http;
import ballerina/log;
import ballerina/time;
import ballerina/uuid;

type InferenceRequest record {|
    string prompt;
    int max_tokens = 256;
    float temperature = 0.7;
    float top_p = 0.9;
    boolean stream = false;
|};

type InferenceResponse record {|
    string request_id;
    string generated_text;
    int tokens_generated;
    float latency_ms;
    string finish_reason;
    string model_id;
|};

type HealthStatus record {|
    string status;
    int active_requests;
    int total_requests;
    float avg_latency_ms;
    string uptime;
|};

// Service state
int totalRequests = 0;
int activeRequests = 0;
float totalLatencyMs = 0.0;
time:Utc startTime = time:utcNow();

service /api/v1 on new http:Listener(8080) {

    // Health check endpoint
    resource function get health() returns HealthStatus {
        float avgLatency = totalRequests > 0 ? totalLatencyMs / <float>totalRequests : 0.0;
        time:Utc now = time:utcNow();
        time:Seconds uptime = time:utcDiffInSeconds(now, startTime);
        return {
            status: "healthy",
            active_requests: activeRequests,
            total_requests: totalRequests,
            avg_latency_ms: avgLatency,
            uptime: uptime.toString() + "s"
        };
    }

    // Inference endpoint
    resource function post infer(@http:Payload InferenceRequest req) returns InferenceResponse|http:InternalServerError {
        string requestId = uuid:createRandomUuid();
        time:Utc startTs = time:utcNow();
        activeRequests += 1;

        log:printInfo("Inference request", request_id = requestId, prompt_len = req.prompt.length());

        // Production inference logic
        string|error result = processInference(req);

        time:Utc endTs = time:utcNow();
        float latency = <float>time:utcDiffInSeconds(endTs, startTs) * 1000.0;
        activeRequests -= 1;
        totalRequests += 1;
        totalLatencyMs += latency;

        if result is error {
            log:printError("Inference failed", request_id = requestId, err = result.message());
            return http:INTERNAL_SERVER_ERROR;
        }

        return {
            request_id: requestId,
            generated_text: result,
            tokens_generated: req.max_tokens,
            latency_ms: latency,
            finish_reason: "stop",
            model_id: "omni-7b"
        };
    }

    // Batch inference
    resource function post batch(@http:Payload InferenceRequest[] requests) returns InferenceResponse[] {
        InferenceResponse[] responses = [];
        foreach InferenceRequest req in requests {
            string requestId = uuid:createRandomUuid();
            string|error result = processInference(req);
            responses.push({
                request_id: requestId,
                generated_text: result is error ? "Error: " + result.message() : result,
                tokens_generated: req.max_tokens,
                latency_ms: 0.0,
                finish_reason: result is error ? "error" : "stop",
                model_id: "omni-7b"
            });
        }
        return responses;
    }
}

function processInference(InferenceRequest req) returns string|error {
    // In production, this calls the OMNI inference engine via FFI
    if req.prompt.length() == 0 {
        return error("Empty prompt");
    }
    return "Generated response for: " + req.prompt.substring(0, int:min(50, req.prompt.length()));
}
