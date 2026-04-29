package omni.events.memgpt;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI MEMGPT: Memory Paging Event Stream (Java)
 * Tracks whenever context blocks are moved from Working Memory (Core) to Archival Memory,
 * providing insight into the agent's context retention capabilities.
 * Source: memgpt/MemGPT
 */
public class MemoryPagingStream {
    private final KafkaProducer<String, String> producer;
    private final String topic = "memgpt-paging-events";

    public MemoryPagingStream(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    public enum PageDirection {
        PAGE_OUT_TO_ARCHIVAL,
        PAGE_IN_TO_CORE
    }

    /**
     * Logs a memory paging event.
     */
    public void logPageEvent(String agentId, PageDirection direction, int tokenCount, String summary) {
        String payload = String.format(
            "{\"agent_id\":\"%s\", \"direction\":\"%s\", \"tokens\":%d, \"summary\":\"%s\", \"ts\":%d}",
            agentId, direction.name(), tokenCount, summary.replace("\"", "\\\""), System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, agentId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log paging event: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
