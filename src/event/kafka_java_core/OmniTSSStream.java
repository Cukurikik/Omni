// Omni TimeSeriesScientist Event Stream (Kafka Java)
// Event Layer: Time series anomaly event processing.
// Ref: Y-Research-SBU/TimeSeriesScientist
package dev.omni.tss;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
public class OmniTSSStream {
    public static void buildTopology(StreamsBuilder builder) {
        KStream<String, String> series = builder.stream("ts-raw-datapoints");
        series.filter((key, val) -> val != null && val.contains("\"anomaly\""))
              .mapValues(v -> v.replace("\"status\":\"detected\"", "\"status\":\"CONFIRMED\""))
              .to("ts-confirmed-anomalies");
    }
}
