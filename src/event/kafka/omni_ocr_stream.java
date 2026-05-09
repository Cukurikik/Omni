package com.omni.event;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;
import java.util.Properties;

public class OmniOcrStream {
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-inverse-dalle-ocr");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "omni-kafka-cluster:9092");

        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> imageStream = builder.stream("omni-image-ingest");

        imageStream
            .filter((key, value) -> value.contains("requires_ocr"))
            .mapValues(value -> "DISPATCH_TO_INVERSE_DALLE_API: " + value)
            .to("omni-ocr-processing");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
        
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
