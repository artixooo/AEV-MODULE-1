package models

import "time"

type AuditLog struct {
	ID        int64     `json:"id"`
	Event     string    `json:"event"`
	UserID    string    `json:"user_id"`
	Action    string    `json:"action"`
	Resource  string    `json:"resource"`
	CreatedAt time.Time `json:"created_at"`
}
