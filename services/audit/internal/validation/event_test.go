package validation

import (
	"testing"

	"audit/internal/models"
)

func TestValidateEvent_ValidEvent(t *testing.T) {
	event := models.AuthenticationEvent{
		EventID:        "event-123",
		EventType:      "user.login",
		UserID:         "user-123",
		OrganizationID: "org-123",
	}

	if err := ValidateEvent(event); err != nil {
		t.Fatalf("expected valid event, got error: %v", err)
	}
}

func TestValidateEvent_MissingEventID(t *testing.T) {
	event := models.AuthenticationEvent{
		EventType:      "user.login",
		UserID:         "user-123",
		OrganizationID: "org-123",
	}

	if err := ValidateEvent(event); err == nil {
		t.Fatal("expected error for missing event ID")
	}
}

func TestValidateEvent_MissingOrganizationID(t *testing.T) {
	event := models.AuthenticationEvent{
		EventID:   "event-123",
		EventType: "user.login",
		UserID:    "user-123",
	}

	if err := ValidateEvent(event); err == nil {
		t.Fatal("expected error for missing organization ID")
	}
}

func TestValidateEvent_MissingUserID(t *testing.T) {
	event := models.AuthenticationEvent{
		EventID:        "event-123",
		EventType:      "user.login",
		OrganizationID: "org-123",
	}

	if err := ValidateEvent(event); err == nil {
		t.Fatal("expected error for missing user ID")
	}
}

func TestHandleInvalidEvent(t *testing.T) {
	event := models.AuthenticationEvent{
		EventID:        "event-123",
		EventType:      "user.login",
		UserID:         "user-123",
		OrganizationID: "",
	}

	validationErr := ValidateEvent(event)
	if validationErr == nil {
		t.Fatal("expected validation error")
	}

	err := HandleInvalidEvent(event, validationErr)
	if err == nil {
		t.Fatal("expected invalid event handling error")
	}
}
