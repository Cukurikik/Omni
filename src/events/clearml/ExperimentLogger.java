package dev.omni.events.clearml;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

public class ExperimentLogger {
    private KafkaProducer<String, String> producer;

    public ExperimentLogger(Properties props) {
        this.producer = new KafkaProducer<>(props);
    }

    public void logMetric(String experimentId, String metricJson) {
        producer.send(new ProducerRecord<>("clearml-metrics", experimentId, metricJson));
    }
}
