// Omni ETO Event Stream (Kafka Streams Java)
// Event Layer: High-throughput trajectory evaluation events.
// Ref: Yifan-Song793/ETO

package dev.omni.eto;

import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;

public class OmniEtoEventStream {
    public static void buildTopology(StreamsBuilder builder) {
        KStream<String, String> trajectories = builder.stream("eto-raw-trajectories");
        trajectories
            .filter((key, value) -> value != null && value.contains("\"reward\""))
            .mapValues(v -> v.replace("\"status\":\"pending\"", "\"status\":\"SCORED\""))
            .to("eto-scored-trajectories");
    }
}
