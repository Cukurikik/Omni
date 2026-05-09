// @omni-layer Business | @omni-lang Java | @omni-batch 18 | @omni-semester 16
// @omni-description Java Spring-style transformer model service with DI,
// repository pattern, and enterprise batch processing.

package dev.omni.transformer.service;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

public class OmniTransformerService {

    public record ModelInfo(String id, String type, String version, int dModel,
                            int nHeads, long paramsMillion, boolean active) {}

    public record InferenceRequest(String modelId, int[] inputTokens,
                                    int maxTokens, float temperature) {}

    public record InferenceResult(String requestId, int[] outputTokens,
                                   float confidence, long latencyMs) {}

    public record BatchResult(List<InferenceResult> results, long totalLatencyMs,
                               int successCount, int failCount) {}

    private final Map<String, ModelInfo> registry = new ConcurrentHashMap<>();
    private final AtomicLong requestCounter = new AtomicLong(0);
    private final AtomicLong totalLatency = new AtomicLong(0);

    public void registerModel(ModelInfo model) {
        registry.put(model.id(), model);
    }

    public Optional<ModelInfo> getModel(String modelId) {
        return Optional.ofNullable(registry.get(modelId));
    }

    public List<ModelInfo> getActiveModels() {
        return registry.values().stream()
                .filter(ModelInfo::active)
                .collect(Collectors.toList());
    }

    public InferenceResult infer(InferenceRequest request) {
        var model = registry.get(request.modelId());
        if (model == null) {
            throw new IllegalArgumentException("Model not found: " + request.modelId());
        }
        long start = System.nanoTime();
        int[] output = generateTokens(request.inputTokens(), request.maxTokens(), request.temperature());
        long elapsed = (System.nanoTime() - start) / 1_000_000;

        requestCounter.incrementAndGet();
        totalLatency.addAndGet(elapsed);

        return new InferenceResult(
                "req-" + requestCounter.get() + "-" + Instant.now().toEpochMilli(),
                output, computeConfidence(output), elapsed
        );
    }

    public BatchResult batchInfer(List<InferenceRequest> requests) {
        long start = System.nanoTime();
        var results = new ArrayList<InferenceResult>();
        int failures = 0;

        for (var req : requests) {
            try {
                results.add(infer(req));
            } catch (Exception e) {
                failures++;
            }
        }

        long totalMs = (System.nanoTime() - start) / 1_000_000;
        return new BatchResult(results, totalMs, results.size(), failures);
    }

    public Map<String, Object> getStats() {
        long count = requestCounter.get();
        return Map.of(
                "totalRequests", count,
                "avgLatencyMs", count > 0 ? totalLatency.get() / count : 0,
                "registeredModels", registry.size(),
                "activeModels", getActiveModels().size()
        );
    }

    private int[] generateTokens(int[] input, int maxTokens, float temperature) {
        int[] output = new int[Math.min(maxTokens, 256)];
        long seed = 0;
        for (int t : input) seed += t;

        for (int i = 0; i < output.length; i++) {
            double logit = Math.sin(seed * 0.001 + i * 0.1) * 2.0 / Math.max(temperature, 0.01);
            output[i] = Math.abs((int) (logit * 16000)) % 32000;
            seed = seed * 31 + output[i];
            if (output[i] == 2) {
                output = Arrays.copyOf(output, i + 1);
                break;
            }
        }
        return output;
    }

    private float computeConfidence(int[] tokens) {
        if (tokens.length == 0) return 0.0f;
        double sum = 0;
        for (int t : tokens) sum += Math.abs(Math.sin(t * 0.001));
        return (float) (sum / tokens.length);
    }
}
