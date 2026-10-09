package validation

import (
	"fmt"
	"strings"

	"audit/internal/models"
)

func ValidateEvent(event models.AuthenticationEvent) error {
	if strings.TrimSpace(event.EventID) == "" {
		return fmt.Errorf("event ID is required")
	}

	if strings.TrimSpace(event.EventType) == "" {
		return fmt.Errorf("event type is required")
	}

	if strings.TrimSpace(event.OrganizationID) == "" {
		return fmt.Errorf("organization ID is required")
	}

	if strings.TrimSpace(event.UserID) == "" {
		return fmt.Errorf("user ID is required")
	}

	return nil
}

func HandleInvalidEvent(event models.AuthenticationEvent, err error) error {
	if err == nil {
		return nil
	}

	return fmt.Errorf(
		"invalid audit event %s: %w",
		event.EventID,
		err,
	)
}
