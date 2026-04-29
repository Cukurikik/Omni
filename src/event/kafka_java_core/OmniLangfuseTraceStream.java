// Omni Langfuse Trace Stream (Kafka Streams / Java)
// Event Layer: High-throughput ingestion and validation of Langfuse observability events.

package dev.omni.langfuse;

import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;

public class OmniLangfuseTraceStream {
    public static void buildTopology(StreamsBuilder builder) {
        KStream<String, String> traceStream = builder.stream("langfuse-raw-traces");

        traceStream
            .filter((key, value) -> value != null && value.contains("\"traceID\""))
            // Deterministic stateless transformation
            .mapValues(value -> value.replace("\"status\":\"pending\"", "\"status\":\"PROCESSED_OMNI\""))
            .to("langfuse-verified-traces");
    }
}
