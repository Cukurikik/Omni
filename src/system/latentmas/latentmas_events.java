// LatentMAS Event Stream Processor
package com.omni.latentmas;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;

public class LatentMASEvents {
    public static void buildTopology(StreamsBuilder builder) {
        KStream<String, String> source = builder.stream("agent-actions");
        source.filter((key, value) -> value.contains("CRITICAL"))
              .to("agent-alerts");
    }
}
