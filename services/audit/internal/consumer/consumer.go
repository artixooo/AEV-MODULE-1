package consumer

import (
	"context"
	"encoding/json"
	"fmt"

	"audit/internal/models"
	"audit/internal/validation"

	"github.com/segmentio/kafka-go"
)

type messageReader interface {
	ReadMessage(context.Context) (kafka.Message, error)
	Close() error
}

type KafkaConsumer struct {
	reader messageReader
}

func NewKafkaConsumer(broker string, topic string, groupID string) *KafkaConsumer {
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers: []string{broker},
		Topic:   topic,
		GroupID: groupID,
	})

	return &KafkaConsumer{
		reader: reader,
	}
}

func (c *KafkaConsumer) ReadMessage(ctx context.Context) ([]byte, error) {
	message, err := c.reader.ReadMessage(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to read Kafka message: %w", err)
	}

	return message.Value, nil
}

func ValidateAndDecodeEvent(data []byte) (models.AuthenticationEvent, error) {
	var event models.AuthenticationEvent

	if err := json.Unmarshal(data, &event); err != nil {
		return models.AuthenticationEvent{}, fmt.Errorf("invalid event JSON: %w", err)
	}

	if err := validation.ValidateEvent(event); err != nil {
		return models.AuthenticationEvent{}, validation.HandleInvalidEvent(event, err)
	}

	return event, nil
}

func (c *KafkaConsumer) ReadAndValidateEvent(ctx context.Context) (models.AuthenticationEvent, error) {
	data, err := c.ReadMessage(ctx)
	if err != nil {
		return models.AuthenticationEvent{}, err
	}

	return ValidateAndDecodeEvent(data)
}

func (c *KafkaConsumer) Close() error {
	return c.reader.Close()
}
