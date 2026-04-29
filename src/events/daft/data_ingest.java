package dev.omni.events.daft;

import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

public class DaftDataIngest {
    
    // OMNI Engine: Streams raw data from Kafka to Daft Rust Core (Zero-Copy)
    public void runIngest() {
        Properties props = new Properties();
        props.put("bootstrap.servers", "localhost:9092");
        props.put("group.id", "daft-ingest-group");
        props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
        props.put("value.deserializer", "org.apache.kafka.common.serialization.ByteArrayDeserializer");

        KafkaConsumer<String, byte[]> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Collections.singletonList("multimodal-raw-stream"));

        while (true) {
            ConsumerRecords<String, byte[]> records = consumer.poll(Duration.ofMillis(100));
            records.forEach(record -> {
                // Pass byte array directly to Rust Daft via JNI
                sendToRustDaftMemoryPointer(record.value());
            });
        }
    }

    private native void sendToRustDaftMemoryPointer(byte[] payload);
}
