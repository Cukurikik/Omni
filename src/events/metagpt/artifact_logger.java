package omni.events.metagpt;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI METAGPT: Artifact Logger (Java)
 * Streams agent-generated artifacts (PRDs, Code, Tests) to a permanent Kafka log
 * for auditability and system memory restoration.
 * Source: geekan/MetaGPT
 */
public class ArtifactLogger {
    private final KafkaProducer<String, String> producer;
    private final String topic = "metagpt-artifacts";

    public ArtifactLogger(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("acks", "all"); // Require full durability for generated code
        
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * @param projectId The UUID of the software project
     * @param role The agent role (e.g., "Engineer")
     * @param artifactType The type (e.g., "Code", "SystemDesign")
     * @param content The actual generated text/code
     */
    public void logArtifact(String projectId, String role, String artifactType, String content) {
        // Escaping for JSON simulation
        String safeContent = content.replace("\"", "\\\"").replace("\n", "\\n");
        
        String payload = String.format(
            "{\"project_id\":\"%s\", \"role\":\"%s\", \"type\":\"%s\", \"content\":\"%s\", \"ts\":%d}",
            projectId, role, artifactType, safeContent, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, projectId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("[OMNI MetaGPT] FATAL: Failed to persist artifact: " + exception.getMessage());
            } else {
                System.out.println("[OMNI MetaGPT] Artifact saved to offset: " + metadata.offset());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
