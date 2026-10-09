package models

import (
	"errors"
	"strings"
)

var (
	ErrMissingEventID       = errors.New("event_id is required")
	ErrMissingEventType     = errors.New("event_type is required")
	ErrMissingEventVersion  = errors.New("event_version is required")
	ErrMissingServiceName   = errors.New("service_name is required")
	ErrMissingAction        = errors.New("action is required")
	ErrMissingStatus        = errors.New("status is required")
	ErrMissingTenantContext = errors.New("tenant context is required")
)

// Validate checks that an audit event contains the required fields.
func (e AuditEvent) Validate() error {
	if strings.TrimSpace(e.EventID) == "" {
		return ErrMissingEventID
	}

	if strings.TrimSpace(e.EventType) == "" {
		return ErrMissingEventType
	}

	if strings.TrimSpace(e.EventVersion) == "" {
		return ErrMissingEventVersion
	}

	if strings.TrimSpace(e.ServiceName) == "" {
		return ErrMissingServiceName
	}

	if strings.TrimSpace(e.Action) == "" {
		return ErrMissingAction
	}

	if strings.TrimSpace(e.Status) == "" {
		return ErrMissingStatus
	}

	if e.TenantID == "" && e.OrganizationID == "" {
		return ErrMissingTenantContext
	}

	return nil
}
