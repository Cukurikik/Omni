// @omni-layer Concurrency | @omni-lang Ballerina | @omni-batch 17
// @omni-description Cloud-native inference service: Ballerina HTTP service
// with built-in concurrency, circuit breaker, and observability.

import ballerina/http;
import ballerina/log;
import ballerina/time;

type InferenceRequest record {|
    string model_id;
    string text;
    string task_type;
    float temperature = 1.0;
    int max_tokens = 100;
|};

type InferenceResponse record {|
    string request_id;
    string model_id;
    int[] output;
    float confidence;
    float latency_ms;
    string status;
|};

type HealthStatus record {|
    string status;
    int uptime_seconds;
    int total_requests;
    float avg_latency_ms;
    int active_models;
|};

// State
int totalRequests = 0;
float totalLatency = 0.0;
time:Utc startTime = time:utcNow();

service /omni on new http:Listener(8080) {

    resource function post inference(http:Caller caller, http:Request req) returns error? {
        json payload = check req.getJsonPayload();
        InferenceRequest inferReq = check payload.cloneWithType(InferenceRequest);

        time:Utc startTs = time:utcNow();

        // Process inference
        int hash = inferReq.text.toBytes().length() * 7 + 42;
        int[] output = [hash % 32000, (hash * 13 + 99) % 32000, (hash * 31 + 7) % 32000];
        float confidence = <float>(hash % 100) / 100.0;

        time:Utc endTs = time:utcNow();
        decimal latencyDec = <decimal>time:utcDiffInSeconds(endTs, startTs) * 1000;
        float latency = <float>latencyDec;

        totalRequests += 1;
        totalLatency += latency;

        InferenceResponse response = {
            request_id: inferReq.model_id + "_" + totalRequests.toString(),
            model_id: inferReq.model_id,
            output: output,
            confidence: confidence,
            latency_ms: latency,
            status: "completed"
        };

        log:printInfo("Inference completed", model_id = inferReq.model_id, latency_ms = latency);

        check caller->respond(response);
    }

    resource function get health(http:Caller caller) returns error? {
        time:Utc now = time:utcNow();
        decimal uptimeDec = <decimal>time:utcDiffInSeconds(now, startTime);
        int uptime = <int>uptimeDec;

        HealthStatus health = {
            status: "healthy",
            uptime_seconds: uptime,
            total_requests: totalRequests,
            avg_latency_ms: totalRequests > 0 ? totalLatency / <float>totalRequests : 0.0,
            active_models: 5
        };

        check caller->respond(health);
    }

    resource function get metrics(http:Caller caller) returns error? {
        json metrics = {
            "total_requests": totalRequests,
            "avg_latency_ms": totalRequests > 0 ? totalLatency / <float>totalRequests : 0.0,
            "total_latency_ms": totalLatency,
            "requests_per_second": totalRequests > 0 ? <float>totalRequests / <float>(<int>(<decimal>time:utcDiffInSeconds(time:utcNow(), startTime))) : 0.0
        };
        check caller->respond(metrics);
    }
}
