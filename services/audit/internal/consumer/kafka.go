package consumer

import (
	"context"
	"fmt"

	"github.com/segmentio/kafka-go"
)

func CheckKafkaConnection(broker, topic string) error {
	conn, err := kafka.DialLeader(
		context.Background(),
		"tcp",
		broker,
		topic,
		0,
	)
	if err != nil {
		return fmt.Errorf("failed to connect to Kafka topic %s: %w", topic, err)
	}

	defer conn.Close()

	return nil
}
