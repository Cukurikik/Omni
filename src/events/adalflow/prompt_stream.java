package omni.events.adalflow;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

/**
 * OMNI ADALFLOW: Prompt Evaluation Stream Consumer (Java Kafka)
 * Listens to continuous streams of generated prompts and evaluations to track optimizer convergence.
 * Source: SylphAI-Inc/AdalFlow
 */
public class PromptStreamConsumer {

    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "adalflow-optimizer-group");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList("adalflow-prompts"));

        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    System.out.printf("Received Prompt Gen: Key = %s, Score Data = %s, Offset = %d%n",
                            record.key(), record.value(), record.offset());
                            
                    // Here we would route the data into TimescaleDB or ElasticSearch 
                    // to visualize the evolution of prompts
                }
            }
        } finally {
            consumer.close();
        }
    }
}
