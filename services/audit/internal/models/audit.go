package models

import "time"

// AuditEvent represents an event that can be recorded by the Audit Service.
type AuditEvent struct {
	EventID        string                 `json:"event_id"`
	EventType      string                 `json:"event_type"`
	EventVersion   string                 `json:"event_version"`
	ServiceName    string                 `json:"service_name"`
	UserID         string                 `json:"user_id,omitempty"`
	TenantID       string                 `json:"tenant_id,omitempty"`
	OrganizationID string                 `json:"organization_id,omitempty"`
	WorkspaceID    string                 `json:"workspace_id,omitempty"`
	ProjectID      string                 `json:"project_id,omitempty"`
	ResourceType   string                 `json:"resource_type,omitempty"`
	ResourceID     string                 `json:"resource_id,omitempty"`
	Action         string                 `json:"action"`
	Status         string                 `json:"status"`
	IPAddress      string                 `json:"ip_address,omitempty"`
	UserAgent      string                 `json:"user_agent,omitempty"`
	RequestID      string                 `json:"request_id,omitempty"`
	Timestamp      time.Time              `json:"timestamp"`
	Metadata       map[string]interface{} `json:"metadata,omitempty"`
}
