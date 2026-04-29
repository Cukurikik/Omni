package omni.events.vllm;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI vLLM: Inference Request Logger (Java Kafka)
 * Emits telemetry for every completed LLM request, including KV cache hit rates.
 * Source: vllm-project/vllm
 */
public class RequestLogger {
    private final KafkaProducer<String, String> producer;
    private final String topic = "vllm-request-logs";

    public RequestLogger(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * Emits inference telemetry.
     */
    public void logRequest(String requestId, int promptTokens, int generatedTokens, 
                           double latencyMs, double cacheHitRate) {
                               
        String payload = String.format(
            "{\"request_id\":\"%s\", \"prompt_tokens\":%d, \"generated_tokens\":%d, \"latency_ms\":%.2f, \"cache_hit_rate\":%.2f, \"ts\":%d}",
            requestId, promptTokens, generatedTokens, latencyMs, cacheHitRate, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, requestId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("vLLM Telemetry Failure: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
