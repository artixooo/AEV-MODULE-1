package models

import (
	"testing"
	"time"
)

func validAuditEvent() AuditEvent {
	return AuditEvent{
		EventID:      "event-123",
		EventType:    EventTypeUserLogin,
		EventVersion: "1.0",
		ServiceName:  "identity",
		TenantID:     "tenant-123",
		UserID:       "user-123",
		Action:       "login",
		Status:       "success",
		Timestamp:    time.Now(),
	}
}

func TestAuditEventValidate(t *testing.T) {
	event := validAuditEvent()

	if err := event.Validate(); err != nil {
		t.Fatalf("expected valid event, got error: %v", err)
	}
}

func TestAuditEventRequiresEventID(t *testing.T) {
	event := validAuditEvent()
	event.EventID = ""

	if err := event.Validate(); err != ErrMissingEventID {
		t.Fatalf("expected ErrMissingEventID, got %v", err)
	}
}

func TestAuditEventRequiresEventType(t *testing.T) {
	event := validAuditEvent()
	event.EventType = ""

	if err := event.Validate(); err != ErrMissingEventType {
		t.Fatalf("expected ErrMissingEventType, got %v", err)
	}
}

func TestAuditEventRequiresTenantContext(t *testing.T) {
	event := validAuditEvent()
	event.TenantID = ""
	event.OrganizationID = ""

	if err := event.Validate(); err != ErrMissingTenantContext {
		t.Fatalf("expected ErrMissingTenantContext, got %v", err)
	}
}

func TestAuditEventAcceptsOrganizationContext(t *testing.T) {
	event := validAuditEvent()
	event.TenantID = ""
	event.OrganizationID = "org-123"

	if err := event.Validate(); err != nil {
		t.Fatalf("expected organization context to be valid, got error: %v", err)
	}
}
func TestAuditEventRequiresEventVersion(t *testing.T) {
	event := validAuditEvent()
	event.EventVersion = ""

	if err := event.Validate(); err != ErrMissingEventVersion {
		t.Fatalf("expected ErrMissingEventVersion, got %v", err)
	}
}

func TestAuditEventRequiresServiceName(t *testing.T) {
	event := validAuditEvent()
	event.ServiceName = ""

	if err := event.Validate(); err != ErrMissingServiceName {
		t.Fatalf("expected ErrMissingServiceName, got %v", err)
	}
}

func TestAuditEventRequiresAction(t *testing.T) {
	event := validAuditEvent()
	event.Action = ""

	if err := event.Validate(); err != ErrMissingAction {
		t.Fatalf("expected ErrMissingAction, got %v", err)
	}
}

func TestAuditEventRequiresStatus(t *testing.T) {
	event := validAuditEvent()
	event.Status = ""

	if err := event.Validate(); err != ErrMissingStatus {
		t.Fatalf("expected ErrMissingStatus, got %v", err)
	}
}
