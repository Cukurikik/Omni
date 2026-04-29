package dev.omni.events;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

public class AgentLogger {
    private KafkaProducer<String, String> producer;

    public AgentLogger(Properties props) {
        this.producer = new KafkaProducer<>(props);
    }

    public void logAction(String agentId, String action) {
        producer.send(new ProducerRecord<>("agent-squad-logs", agentId, action));
    }
}
