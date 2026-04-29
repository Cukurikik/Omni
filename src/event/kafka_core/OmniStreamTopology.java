package omni.event.streams;

import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import java.util.Optional;

public class OmniStreamTopology {
    /**
     * Kafka Streams Topology for Omni Event Sourcing.
     * Enforces Monadic Result handling via Java Optional.
     */
    public void buildTopology(StreamsBuilder builder) {
        KStream<String, byte[]> inputStream = builder.stream("omni-events-in");

        inputStream
            .mapValues(value -> processPayload(value))
            .filter((key, value) -> value.isPresent())
            .mapValues(value -> value.get())
            .to("omni-events-out");
    }

    private Optional<byte[]> processPayload(byte[] payload) {
        if (payload == null || payload.length == 0) {
            return Optional.empty();
        }
        // Deterministic transformation
        return Optional.of(payload);
    }
}
