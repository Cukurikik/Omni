package dev.omni.events;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import java.util.Properties;

public class BacktestStream {
    private KafkaProducer<String, String> producer;

    public BacktestStream(Properties props) {
        this.producer = new KafkaProducer<>(props);
    }

    public void streamTick(String symbol, double price) {
        producer.send(new ProducerRecord<>("vectorbt-ticks", symbol, String.valueOf(price)));
    }
}
