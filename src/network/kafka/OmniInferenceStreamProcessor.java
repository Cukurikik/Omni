// OMNI Event Layer — Kafka Streams Inference Event Processor
// Real-time inference event processing and analytics pipeline.

package dev.omni.streaming;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.*;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.state.KeyValueStore;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.time.Duration;
import java.util.Properties;

public class OmniInferenceStreamProcessor {

    private static final String INPUT_TOPIC = "omni.inference.requests";
    private static final String OUTPUT_TOPIC = "omni.inference.analytics";
    private static final String ERROR_TOPIC = "omni.inference.errors";
    private static final ObjectMapper mapper = new ObjectMapper();

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-inference-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");

        StreamsBuilder builder = new StreamsBuilder();

        // Source: inference request events
        KStream<String, String> requests = builder.stream(INPUT_TOPIC);

        // Branch: valid vs error
        KStream<String, String>[] branches = requests.branch(
            (key, value) -> isValidRequest(value),
            (key, value) -> true
        );

        KStream<String, String> validRequests = branches[0];
        KStream<String, String> invalidRequests = branches[1];

        // Route errors
        invalidRequests.to(ERROR_TOPIC);

        // Compute: per-model latency statistics (tumbling 1-minute windows)
        validRequests
            .groupBy((key, value) -> extractModelId(value))
            .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
            .aggregate(
                () -> "{\"count\":0,\"total_latency\":0,\"max_latency\":0}",
                (modelId, value, aggregate) -> aggregateMetrics(aggregate, value),
                Materialized.with(Serdes.String(), Serdes.String())
            )
            .toStream()
            .map((windowedKey, value) -> KeyValue.pair(windowedKey.key(), value))
            .to(OUTPUT_TOPIC);

        // Count: requests per model (global)
        validRequests
            .groupBy((key, value) -> extractModelId(value))
            .count(Materialized.as("model-request-counts"))
            .toStream()
            .mapValues(count -> "{\"total_requests\":" + count + "}")
            .to("omni.inference.model-counts");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.setUncaughtExceptionHandler((t, e) -> {
            System.err.println("Stream error: " + e.getMessage());
            return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.REPLACE_THREAD;
        });

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
        streams.start();
        System.out.println("OMNI Inference Stream Processor started");
    }

    private static boolean isValidRequest(String value) {
        try {
            JsonNode node = mapper.readTree(value);
            return node.has("model_id") && node.has("latency_ms");
        } catch (Exception e) { return false; }
    }

    private static String extractModelId(String value) {
        try {
            return mapper.readTree(value).get("model_id").asText();
        } catch (Exception e) { return "unknown"; }
    }

    private static String aggregateMetrics(String aggregate, String value) {
        try {
            JsonNode agg = mapper.readTree(aggregate);
            JsonNode val = mapper.readTree(value);
            long count = agg.get("count").asLong() + 1;
            double totalLat = agg.get("total_latency").asDouble() + val.get("latency_ms").asDouble();
            double maxLat = Math.max(agg.get("max_latency").asDouble(), val.get("latency_ms").asDouble());
            return String.format("{\"count\":%d,\"total_latency\":%.2f,\"max_latency\":%.2f,\"avg_latency\":%.2f}",
                count, totalLat, maxLat, totalLat / count);
        } catch (Exception e) { return aggregate; }
    }
}
