package models

import "time"

// AuthenticationEvent represents an authentication-related event
// that can be received by the Audit Service.
type AuthenticationEvent struct {
	EventID        string                 `json:"event_id"`
	EventType      string                 `json:"event_type"`
	UserID         string                 `json:"user_id"`
	OrganizationID string                 `json:"organization_id"`
	IPAddress      string                 `json:"ip_address"`
	UserAgent      string                 `json:"user_agent"`
	Timestamp      time.Time              `json:"timestamp"`
	Metadata       map[string]interface{} `json:"metadata"`
}
