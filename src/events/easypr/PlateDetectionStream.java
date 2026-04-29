package dev.omni.events.easypr;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

public class PlateDetectionStream {
    private KafkaProducer<String, String> producer;

    public PlateDetectionStream(Properties props) {
        this.producer = new KafkaProducer<>(props);
    }

    public void emitDetection(String cameraId, String plateNumber) {
        producer.send(new ProducerRecord<>("easypr-detections", cameraId, plateNumber));
    }
}
