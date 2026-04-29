package dev.omniframework.beta9;

// Beta9 serverless execution events
// Java Kafka stream

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;

public class Beta9Events {
    public static void main(String[] args) {
        StreamsBuilder builder = new StreamsBuilder();
        builder.stream("beta9-jobs")
               .filter((k, v) -> v != null)
               .to("beta9-processed");
    }
}
