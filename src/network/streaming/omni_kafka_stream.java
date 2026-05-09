package com.omni.streaming;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;

import java.util.Properties;

/**
 * OMNI Event & Streaming Layer
 * Kafka Streams application for real-time ingestion and tokenization of high-throughput data streams
 * feeding directly into the Omni Polyglot Inference Engine.
 */
public class OmniKafkaStreamProcessor {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-inference-stream");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.ByteArray().getClass());

        StreamsBuilder builder = new StreamsBuilder();
        
        // Ingest raw byte arrays from IoT or web sensors
        KStream<String, byte[]> rawInput = builder.stream("omni-raw-sensors");

        // Pass through Omni native bridge for zero-copy tensor projection
        KStream<String, byte[]> processedTensors = rawInput.mapValues(value -> {
            return OmniNativeBridge.processTensor(value);
        });

        processedTensors.to("omni-inference-results");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        // Add shutdown hook to respond to SIGTERM and gracefully close Kafka Streams
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
