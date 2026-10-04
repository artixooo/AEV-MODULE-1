package repository

import "context"

// SaveConfigInput carries everything needed to create or update a row in
// `configuration`. ChangedBy/ChangeReason are optional but, when
// provided, are written to `configuration_history` alongside the change.
type SaveConfigInput struct {
	ConfigKey      string
	ConfigValue    string
	DataType       DataType
	Scope          Scope
	OrganizationID *string
	WorkspaceID    *string
	ProjectID      *string
	Description    string
	IsEditable     bool

	// Audit fields — optional, but recommended on every write.
	ChangedBy    *string // UUID of the acting user/service
	ChangeReason string
}

// SaveFeatureFlagInput carries everything needed to create or update a
// row in `feature_flags`.
type SaveFeatureFlagInput struct {
	FlagKey           string
	FlagName          string
	Description       string
	IsEnabled         bool
	Scope             Scope
	OrganizationID    *string
	WorkspaceID       *string
	ProjectID         *string
	RolloutPercentage int
}

// ListFilter narrows a List* query down to a scope and/or a specific
// organization/workspace/project. Leave a field nil/empty to not filter
// on it.
type ListFilter struct {
	Scope          Scope
	OrganizationID *string
	WorkspaceID    *string
	ProjectID      *string
}

// Repository is the data-access contract for the configuration service,
// matching the approved 3-table schema: configuration, feature_flags,
// and configuration_history.
type Repository interface {
	// Configuration
	GetConfig(ctx context.Context, key string) (*Configuration, error)
	SaveConfig(ctx context.Context, input SaveConfigInput) (*Configuration, error)
	DeleteConfig(ctx context.Context, key string) error
	ListConfigurations(ctx context.Context, filter ListFilter) ([]Configuration, error)
	GetConfigurationHistory(ctx context.Context, configurationID string) ([]ConfigurationHistory, error)

	// Feature flags
	GetFeatureFlag(ctx context.Context, flagKey string) (*FeatureFlag, error)
	SaveFeatureFlag(ctx context.Context, input SaveFeatureFlagInput) (*FeatureFlag, error)
	ListFeatureFlags(ctx context.Context, filter ListFilter) ([]FeatureFlag, error)
}
