package omni.events.localai;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI LOCALAI: Metrics Stream (Java)
 * Streams token generation velocity and hardware utilization metrics to Kafka for dashboarding.
 * Source: mudler/LocalAI
 */
public class MetricsStream {
    private final KafkaProducer<String, String> producer;
    private final String topic = "localai-metrics";

    public MetricsStream(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("acks", "1"); // Fire and forget for telemetry
        
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * @param modelId The ID of the model being run
     * @param tokensPerSecond Generation speed
     * @param ramUsageMb Memory consumption
     */
    public void emitHardwareMetric(String modelId, double tokensPerSecond, int ramUsageMb) {
        String payload = String.format(
            "{\"model_id\":\"%s\", \"tps\":%.2f, \"ram_mb\":%d, \"ts\":%d}",
            modelId, tokensPerSecond, ramUsageMb, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, modelId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                // Monadic fallback: log to stderr if Kafka is down, do not crash inference
                System.err.println("[OMNI LocalAI] Telemetry emit failed: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
