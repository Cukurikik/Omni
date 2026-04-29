package omni.events.mmsegmentation;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

/**
 * OMNI MMSEGMENTATION: Training Progress Stream (Java Kafka)
 * Emits telemetry per-epoch including mIoU (Mean Intersection over Union) and Dice Loss metrics.
 * Source: open-mmlab/mmsegmentation
 */
public class TrainingProgressStream {
    private final KafkaProducer<String, String> producer;
    private final String topic = "mmseg-training-progress";

    public TrainingProgressStream(String brokerList) {
        Properties props = new Properties();
        props.put("bootstrap.servers", brokerList);
        props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
        this.producer = new KafkaProducer<>(props);
    }

    /**
     * Emits training progress for a specific epoch.
     */
    public void logEpoch(String runId, int epoch, double trainLoss, double valLoss, double mIoU) {
        String payload = String.format(
            "{\"run_id\":\"%s\", \"epoch\":%d, \"train_loss\":%.4f, \"val_loss\":%.4f, \"mIoU\":%.4f, \"ts\":%d}",
            runId, epoch, trainLoss, valLoss, mIoU, System.currentTimeMillis()
        );

        ProducerRecord<String, String> record = new ProducerRecord<>(topic, runId, payload);
        
        producer.send(record, (metadata, exception) -> {
            if (exception != null) {
                System.err.println("Failed to log training progress: " + exception.getMessage());
            }
        });
    }

    public void close() {
        producer.flush();
        producer.close();
    }
}
