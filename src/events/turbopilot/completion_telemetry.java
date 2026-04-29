package omni.events.turbopilot;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI TURBOPILOT: Completion Telemetry (Java)
 * Tracks the "Acceptance Rate" of local LLM code completions to monitor model quality over time.
 * Source: ravenscroftj/turbopilot
 */
public class CompletionTelemetry {
    private final KafkaProducer<String, String> producer;
    private final String topic = "turbopilot-telemetry";

    public CompletionTelemetry(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    public enum Action {
        SHOWN,
        ACCEPTED,
        REJECTED
    }

    /**
     * Emits a telemetry event when a user interacts with a code completion suggestion.
     */
    public void logAction(String sessionId, String completionId, Action action, int tokensGenerated) {
        String payload = String.format(
            "{\"session_id\":\"%s\", \"comp_id\":\"%s\", \"action\":\"%s\", \"tokens\":%d, \"ts\":%d}",
            sessionId, completionId, action.name(), tokensGenerated, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, sessionId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log Turbopilot telemetry: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
