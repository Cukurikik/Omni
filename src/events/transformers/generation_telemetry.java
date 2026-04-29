package omni.events.transformers;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI TRANSFORMERS: Generation Telemetry Stream (Java)
 * Emits real-time tokens-per-second (tok/s) and latency metrics for monitoring LLM serving health.
 * Source: huggingface/transformers
 */
public class GenerationTelemetry {
    private final KafkaProducer<String, String> producer;
    private final String topic = "transformer-generation-metrics";

    public GenerationTelemetry(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * Emits generation statistics.
     */
    public void logGeneration(String requestId, String modelName, int promptLength, 
                              int generatedLength, double totalTimeMs) {
        
        double tokensPerSecond = (generatedLength / (totalTimeMs / 1000.0));
        
        String payload = String.format(
            "{\"req_id\":\"%s\", \"model\":\"%s\", \"prompt_len\":%d, \"gen_len\":%d, \"time_ms\":%.2f, \"tok_s\":%.2f, \"ts\":%d}",
            requestId, modelName, promptLength, generatedLength, totalTimeMs, tokensPerSecond, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, modelName, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log generation telemetry: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
