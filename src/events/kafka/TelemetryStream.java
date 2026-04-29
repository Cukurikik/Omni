package dev.omni.events;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import java.util.Properties;

public class TelemetryStream {
    public static void buildStream(Properties props) {
        StreamsBuilder builder = new StreamsBuilder();
        KStream<String, String> telemetry = builder.stream("omni-telemetry");
        
        telemetry.filter((key, value) -> value.contains("error"))
                 .to("omni-alerts");
                 
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
    }
}
