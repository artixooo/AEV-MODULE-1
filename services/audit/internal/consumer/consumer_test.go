package consumer

import (
	"context"
	"testing"

	"github.com/segmentio/kafka-go"
)

type mockKafkaReader struct {
	message kafka.Message
	err     error
}

func (m *mockKafkaReader) ReadMessage(context.Context) (kafka.Message, error) {
	return m.message, m.err
}

func (m *mockKafkaReader) Close() error {
	return nil
}

func newTestConsumer(data []byte) *KafkaConsumer {
	return &KafkaConsumer{
		reader: &mockKafkaReader{
			message: kafka.Message{
				Value: data,
			},
		},
	}
}

func TestReadAndValidateEvent_ValidJSON(t *testing.T) {
	data := []byte(`{
		"event_id": "event-123",
		"event_type": "user.login",
		"user_id": "user-123",
		"organization_id": "org-123"
	}`)

	consumer := newTestConsumer(data)

	event, err := consumer.ReadAndValidateEvent(context.Background())
	if err != nil {
		t.Fatalf("expected valid event, got error: %v", err)
	}

	if event.EventID != "event-123" {
		t.Fatalf("expected event ID event-123, got %s", event.EventID)
	}

	if event.EventType != "user.login" {
		t.Fatalf("expected event type user.login, got %s", event.EventType)
	}
}

func TestReadAndValidateEvent_MalformedJSON(t *testing.T) {
	data := []byte(`{
		"event_id": "event-123",
		"event_type": "user.login",
		"user_id": "user-123",
		"organization_id": "org-123"
	`)

	consumer := newTestConsumer(data)

	_, err := consumer.ReadAndValidateEvent(context.Background())
	if err == nil {
		t.Fatal("expected error for malformed JSON")
	}
}

func TestReadAndValidateEvent_ValidationFailure(t *testing.T) {
	data := []byte(`{
		"event_id": "event-123",
		"event_type": "user.login",
		"user_id": "",
		"organization_id": "org-123"
	}`)

	consumer := newTestConsumer(data)

	_, err := consumer.ReadAndValidateEvent(context.Background())
	if err == nil {
		t.Fatal("expected validation error")
	}
}
