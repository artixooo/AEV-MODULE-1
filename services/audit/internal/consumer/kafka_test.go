package consumer

import (
	"os"
	"testing"
)

func TestKafkaConfiguration(t *testing.T) {
	broker := os.Getenv("KAFKA_BROKERS")
	topic := os.Getenv("KAFKA_TOPIC_AUDIT")

	if broker == "" {
		t.Fatal("KAFKA_BROKERS must not be empty")
	}

	if topic == "" {
		t.Fatal("KAFKA_TOPIC_AUDIT must not be empty")
	}
}

func TestKafkaConnectivity(t *testing.T) {
	if os.Getenv("RUN_KAFKA_INTEGRATION") != "true" {
		t.Skip("Kafka integration test disabled")
	}

	broker := os.Getenv("KAFKA_BROKERS")
	topic := os.Getenv("KAFKA_TOPIC_AUDIT")

	if err := CheckKafkaConnection(broker, topic); err != nil {
		t.Fatalf("Kafka connectivity check failed: %v", err)
	}
}
