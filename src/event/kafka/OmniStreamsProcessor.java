package com.omni.event;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;
import java.util.Properties;

public class OmniStreamsProcessor {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-telemetry-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka.omni.internal:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();
        
        // Read from GPU temperature sensor topic
        KStream<String, String> telemetryStream = builder.stream("omni.hardware.gpu.temp");

        // Filter high temperatures and route to alerts
        telemetryStream
            .filter((key, value) -> Double.parseDouble(value) > 85.0)
            .mapValues(value -> "CRITICAL TEMP: " + value)
            .to("omni.alerts.hardware");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
