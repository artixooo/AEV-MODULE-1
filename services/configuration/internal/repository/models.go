package repository

import "time"

// Scope identifies which level of the org hierarchy a configuration row
// or feature flag applies to. A row's *_id columns are only meaningful
// for scopes at or below that level (e.g. a WORKSPACE-scoped row sets
// organization_id and workspace_id, but not project_id).
type Scope string

const (
	ScopeGlobal       Scope = "GLOBAL"
	ScopeOrganization Scope = "ORGANIZATION"
	ScopeWorkspace    Scope = "WORKSPACE"
	ScopeProject      Scope = "PROJECT"
)

// DataType describes how config_value should be interpreted/parsed by
// callers. Stored as a plain string column, but typed here to avoid
// stringly-typed call sites.
type DataType string

const (
	DataTypeString DataType = "STRING"
	DataTypeInt    DataType = "INT"
	DataTypeFloat  DataType = "FLOAT"
	DataTypeBool   DataType = "BOOL"
	DataTypeJSON   DataType = "JSON"
)

// Configuration mirrors a row in the `configuration` table.
type Configuration struct {
	ID             string // UUID
	ConfigKey      string
	ConfigValue    string
	DataType       DataType
	Scope          Scope
	OrganizationID *string // UUID, nil unless scope is ORGANIZATION/WORKSPACE/PROJECT
	WorkspaceID    *string // UUID, nil unless scope is WORKSPACE/PROJECT
	ProjectID      *string // UUID, nil unless scope is PROJECT
	Description    string
	IsEditable     bool
	CreatedAt      time.Time
	UpdatedAt      time.Time
}

// FeatureFlag mirrors a row in the `feature_flags` table.
type FeatureFlag struct {
	ID                string // UUID
	FlagKey           string
	FlagName          string
	Description       string
	IsEnabled         bool
	Scope             Scope
	OrganizationID    *string // UUID
	WorkspaceID       *string // UUID
	ProjectID         *string // UUID
	RolloutPercentage int
	CreatedAt         time.Time
	UpdatedAt         time.Time
}

// ConfigurationHistory mirrors a row in the `configuration_history` table.
// One row is written every time a `configuration` row is created or
// updated, forming an audit trail.
type ConfigurationHistory struct {
	ID              string // UUID
	ConfigurationID string // UUID, FK -> configuration.id
	OldValue        *string
	NewValue        string
	ChangedBy       *string // UUID of the user/service that made the change
	ChangeReason    string
	ChangedAt       time.Time
}
