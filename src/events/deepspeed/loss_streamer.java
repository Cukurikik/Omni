package omni.events.deepspeed;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI DEEPSPEED: Distributed Training Loss Streamer (Java)
 * High-throughput Kafka producer for emitting training metrics (loss, throughput, rank states) 
 * from multi-GPU/multi-node clusters to a central telemetry sink.
 * Source: microsoft/DeepSpeed
 */
public class LossStreamer {
    private final KafkaProducer<String, String> producer;
    private final String topic;

    public LossStreamer(String brokerList, String topicName) {
        this.topic = topicName;
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        
        // Optimize for high throughput rather than lowest latency
        props.put("linger.ms", 10);
        props.put("batch.size", 65536);
        props.put("compression.type", "lz4");

        this.producer = new KafkaProducer<>(props);
    }

    /**
     * Emits the loss metric for a specific rank at a specific global step.
     */
    public void emitLoss(int rank, int globalStep, double lossValue, double tflops) {
        String key = "rank_" + rank;
        String payload = String.format(
            "{\"rank\":%d, \"step\":%d, \"loss\":%.6f, \"tflops\":%.2f, \"timestamp\":%d}",
            rank, globalStep, lossValue, tflops, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, payload);
        
        // Fire and forget (errors logged internally by Kafka client)
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("[DeepSpeed Telemetry] Failed to send metric: " + exception.getMessage());
            }
        });
    }

    public void shutdown() {
        producer.flush();
        producer.close();
    }
}
