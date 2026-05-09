// OMNI Framework - Kafka Streams for Crypto Sentiment
// Java implementation to process real-time FinBERT streams

package dev.omni.streaming;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;

import java.util.Properties;

public class OmniCryptoSentimentStream {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-crypto-sentiment");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "omni-kafka:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        StreamsBuilder builder = new StreamsBuilder();
        
        // Read raw signals from Python FinBERT worker
        KStream<String, String> rawSignals = builder.stream("omni.crypto.signals.raw");

        // Filter out HOLD signals, keep only BUY/SELL for alerts
        KStream<String, String> actionableSignals = rawSignals.filter((key, value) -> 
            value.contains("\"BUY\"") || value.contains("\"SELL\"")
        );

        // Output to alert topic
        actionableSignals.to("omni.crypto.signals.alerts");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
