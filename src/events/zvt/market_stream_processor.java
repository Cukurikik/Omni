package omni.events.zvt;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;

import java.time.Duration;
import java.util.Properties;

/**
 * OMNI ZVT: Market Stream Processor (Java Kafka Streams)
 * High-throughput, real-time aggregation of financial tick data for quantitative factors.
 * Source: zvtvz/zvt
 */
public class MarketStreamProcessor {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "omni-zvt-market-processor");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.Double().getClass());

        StreamsBuilder builder = new StreamsBuilder();

        // Consume raw tick prices: Key = Ticker (e.g., AAPL), Value = Price
        KStream<String, Double> tickStream = builder.stream("zvt-raw-ticks");

        // Compute 1-minute Volume Weighted Average Price (VWAP) or simple moving average
        // Here we do a simple windowed aggregation: max and min prices (Candlestick generation)
        tickStream
            .groupByKey()
            .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
            .aggregate(
                () -> "0.0,0.0", // Initial state: min,max
                (key, newPrice, agg) -> {
                    String[] parts = agg.split(",");
                    double min = Double.parseDouble(parts[0]);
                    double max = Double.parseDouble(parts[1]);
                    
                    if (min == 0.0 || newPrice < min) min = newPrice;
                    if (newPrice > max) max = newPrice;
                    
                    return min + "," + max;
                },
                org.apache.kafka.streams.kstream.Materialized.with(Serdes.String(), Serdes.String())
            )
            .toStream()
            .map((Windowed<String> key, String value) -> {
                // Map back to a standard format for downstream consumption
                String outKey = key.key() + "@" + key.window().start();
                return new org.apache.kafka.streams.KeyValue<>(outKey, value);
            })
            .to("zvt-minute-candles", org.apache.kafka.streams.kstream.Produced.with(Serdes.String(), Serdes.String()));

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();

        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));
    }
}
