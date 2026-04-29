package omni.events.kubeflow;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;

import java.util.Properties;
import java.util.concurrent.Future;

/**
 * OMNI KUBEFLOW: Metric Logger (Java Kafka Producer)
 * Emits pipeline execution metrics (loss, accuracy, duration) into the event stream for real-time dashboarding.
 * Source: kubeflow/pipelines
 */
public class MetricLogger {
    private final KafkaProducer<String, String> producer;
    private final String topic;

    public MetricLogger(String brokers, String topic) {
        this.topic = topic;
        Properties props = new Properties();
        props.put("bootstrap.servers", brokers);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        // Acks = all for high durability of metric data
        props.put("acks", "all");
        
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * Logs a metric. Returns an Optional-like wrapper around the Kafka Future.
     * Monadic handling implies callers must deal with potential transmission exceptions.
     */
    public Future<RecordMetadata> logMetric(String runId, String metricName, double value, long timestampMs) {
        // Construct JSON payload
        String payload = String.format("{\"run_id\":\"%s\",\"metric\":\"%s\",\"value\":%f,\"timestamp\":%d}",
                runId, metricName, value, timestampMs);

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, runId, payload);
        
        // Asynchronous send
        return producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log metric: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
