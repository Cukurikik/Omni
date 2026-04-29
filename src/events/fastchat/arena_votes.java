package omni.events.fastchat;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI FASTCHAT: Arena Votes Stream (Java Kafka)
 * Emits user voting telemetry (A is better, B is better, Tie, Both Bad) to calculate Elo ratings.
 * Source: lm-sys/FastChat
 */
public class ArenaVotesStream {
    private final KafkaProducer<String, String> producer;
    private final String topic = "fastchat-arena-votes";

    public ArenaVotesStream(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    public enum VoteChoice {
        MODEL_A,
        MODEL_B,
        TIE,
        BOTH_BAD
    }

    /**
     * Emits a vote event for leaderboard calculation.
     */
    public void logVote(String conversationId, String modelA, String modelB, VoteChoice choice) {
        String payload = String.format(
            "{\"conv_id\":\"%s\", \"model_a\":\"%s\", \"model_b\":\"%s\", \"winner\":\"%s\", \"ts\":%d}",
            conversationId, modelA, modelB, choice.name(), System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, conversationId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log FastChat arena vote: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
