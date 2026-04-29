package dev.omni.events.tsai;

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;

import java.util.Properties;

public class TimeSeriesStreamProcessor {
    public static void startStream(Properties props) {
        StreamsBuilder builder = new StreamsBuilder();
        
        KStream<String, String> sensorData = builder.stream("raw-sensor-data");
        
        // Pass to tsai Python compute layer via OMNI RPC Bridge
        sensorData.mapValues(value -> "tsai_inference_pipeline(" + value + ")")
                  .to("processed-sensor-classifications");

        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
    }
}
