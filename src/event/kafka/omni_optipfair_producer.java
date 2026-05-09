// OMNI Framework - Java Kafka Producer for Optipfair Bias Metrics
package com.omni.event;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;

import java.util.Properties;

public class OmniOptipfairProducer {
    private final KafkaProducer<String, String> producer;
    private final String topic;

    public OmniOptipfairProducer(String bootstrapServers, String topic) {
        this.topic = topic;
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        
        this.producer = new KafkaProducer<>(props);
    }

    public void publishBiasMetric(String modelId, String biasReportJson) {
        ProducerRecord<String, String> record = new ProducerRecord<>(topic, modelId, biasReportJson);
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("OMNI Optipfair Kafka Error: " + exception.getMessage());
            } else {
                System.out.println("Published bias metric to partition " + metadata.partition() + " at offset " + metadata.offset());
            }
        });
    }

    public void close() {
        producer.close();
    }
}
