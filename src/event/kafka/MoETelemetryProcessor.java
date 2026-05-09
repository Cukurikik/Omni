package dev.omni.telemetry;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * OMNI Framework - Kafka Telemetry Processor (Java)
 * Consumes raw token routing events, aggregates load per expert in real-time,
 * and produces scaling signals if an expert becomes a bottleneck.
 */
public class MoETelemetryProcessor {

    private static final String INPUT_TOPIC = "omni.moe.raw_routing";
    private static final String OUTPUT_TOPIC = "omni.moe.expert_load_alarms";
    private static final long LOAD_THRESHOLD = 500_000; // Tokens per minute threshold

    public static void main(String[] args) {
        System.out.println("OMNI Java: Starting MoE Telemetry Processor...");

        Properties props = new Properties();
        props.put("bootstrap.servers", "omni-kafka-broker:9092");
        props.put("group.id", "moe-aggregator-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);

        consumer.subscribe(Collections.singletonList(INPUT_TOPIC));

        ConcurrentHashMap<String, AtomicLong> expertLoadWindow = new ConcurrentHashMap<>();

        try {
            while (true) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    // Assume payload format: "expert_id,tokens_routed" e.g., "exp_5,128"
                    String[] parts = record.value().split(",");
                    if (parts.length == 2) {
                        String expertId = parts[0];
                        long tokens = Long.parseLong(parts[1]);

                        expertLoadWindow.putIfAbsent(expertId, new AtomicLong(0));
                        long currentLoad = expertLoadWindow.get(expertId).addAndGet(tokens);

                        if (currentLoad > LOAD_THRESHOLD) {
                            String alarmMsg = String.format("{\"expert_id\": \"%s\", \"load\": %d, \"action\": \"scale_up\"}", expertId, currentLoad);
                            producer.send(new ProducerRecord<>(OUTPUT_TOPIC, expertId, alarmMsg));
                            System.out.println("OMNI Java: ALARM triggered for " + expertId);
                            // Reset window after alarm
                            expertLoadWindow.get(expertId).set(0);
                        }
                    }
                }
            }
        } finally {
            consumer.close();
            producer.close();
        }
    }
}
