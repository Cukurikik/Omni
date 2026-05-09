// OMNI Framework - Go NSQ Publisher for TableFormer
package nsq

import (
	"log"

	"github.com/nsqio/go-nsq"
)

func publishTableEvent(nsqdAddr string, topic string, payload []byte) {
	config := nsq.NewConfig()
	producer, err := nsq.NewProducer(nsqdAddr, config)
	if err != nil {
		log.Fatal("OMNI NSQ Could not connect:", err)
	}
	defer producer.Stop()

	err = producer.Publish(topic, payload)
	if err != nil {
		log.Fatal("OMNI NSQ Publish error:", err)
	}

	log.Println("OMNI NSQ: Published TableFormer event to topic", topic)
}

// Example usage
// publishTableEvent("127.0.0.1:4150", "omni_tableformer_events", []byte(`{"status": "encoded", "table_id": "tbl_001"}`))

