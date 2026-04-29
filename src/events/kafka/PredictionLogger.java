package dev.omni.events;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

public class PredictionLogger {
    private KafkaProducer<String, String> producer;

    public PredictionLogger(Properties props) {
        this.producer = new KafkaProducer<>(props);
    }

    public void logPrediction(String modelId, String prediction) {
        producer.send(new ProducerRecord<>("omni-predictions", modelId, prediction));
    }
    
    public void close() {
        producer.close();
    }
}
