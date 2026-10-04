// Package configservice provides the tenant-scoped Configuration
// Management service layer for Week 6 — distinct Create/Retrieve/
// Update/Delete semantics, validation, versioning, Policy authorization,
// and audit integration, built on top of the existing repository and
// cache layers.
package configservice

import (
	"context"
	"errors"

	"configuration/internal/repository"
)

// ErrAlreadyExists is returned by Create when a config_key already has a
// row — Create is intentionally NOT an upsert, unlike repository.SaveConfig.
var ErrAlreadyExists = errors.New("configservice: configuration already exists")

// ErrUnauthorized is returned when the Authorizer rejects an operation.
var ErrUnauthorized = errors.New("configservice: not authorized")

// Service wraps a repository.Repository with Week 6's configuration
// management semantics: real Create/Update distinction, validation,
// versioning (via configuration_history), authorization, and audit.
type Service struct {
	repo       repository.Repository
	authorizer Authorizer
	auditor    Auditor
}

// New builds a Service. authorizer and auditor may be nil, in which case
// NoopAuthorizer (allow everything) and NoopAuditor (log nothing) are
// used — callers MUST supply real implementations before this reaches
// production, per the "Integrate Policy authorization" and "Audit
// configuration changes through the Audit contract" tasks. The nil
// defaults exist so this package compiles and is testable before the
// Policy/Audit contracts are finalized.
func New(repo repository.Repository, authorizer Authorizer, auditor Auditor) *Service {
	if authorizer == nil {
		authorizer = NoopAuthorizer{}
	}
	if auditor == nil {
		auditor = NoopAuditor{}
	}
	return &Service{repo: repo, authorizer: authorizer, auditor: auditor}
}

// Actor identifies who is performing an operation, for authorization and
// audit purposes.
type Actor struct {
	UserID         string
	OrganizationID string
}

// Create inserts a brand-new configuration entry. Fails with
// ErrAlreadyExists if config_key is already in use.
func (s *Service) Create(ctx context.Context, actor Actor, input repository.SaveConfigInput) (*repository.Configuration, error) {
	if err := s.authorize(ctx, actor, ActionCreate, input.ConfigKey); err != nil {
		return nil, err
	}
	if err := ValidateConfigInput(input); err != nil {
		return nil, err
	}
	if err := requireTenantMatch(actor, input.OrganizationID); err != nil {
		return nil, err
	}

	if _, err := s.repo.GetConfig(ctx, input.ConfigKey); err == nil {
		return nil, ErrAlreadyExists
	} else if !errors.Is(err, repository.ErrNotFound) {
		return nil, err
	}

	saved, err := s.repo.SaveConfig(ctx, input)
	if err != nil {
		return nil, err
	}
	s.auditor.RecordConfigChange(ctx, AuditEvent{
		Action: ActionCreate, Actor: actor, ConfigKey: input.ConfigKey,
		NewValue: input.ConfigValue,
	})
	return saved, nil
}

// Get retrieves a configuration entry by key, after confirming the actor
// is authorized to read it.
func (s *Service) Get(ctx context.Context, actor Actor, key string) (*repository.Configuration, error) {
	if err := s.authorize(ctx, actor, ActionRead, key); err != nil {
		return nil, err
	}
	cfg, err := s.repo.GetConfig(ctx, key)
	if err != nil {
		return nil, err
	}
	if err := requireTenantMatchPtr(actor, cfg.OrganizationID); err != nil {
		return nil, err
	}
	return cfg, nil
}

// Update modifies an existing configuration entry. Fails with
// repository.ErrNotFound if config_key doesn't already exist.
func (s *Service) Update(ctx context.Context, actor Actor, input repository.SaveConfigInput) (*repository.Configuration, error) {
	if err := s.authorize(ctx, actor, ActionUpdate, input.ConfigKey); err != nil {
		return nil, err
	}
	if err := ValidateConfigInput(input); err != nil {
		return nil, err
	}
	if err := requireTenantMatch(actor, input.OrganizationID); err != nil {
		return nil, err
	}

	existing, err := s.repo.GetConfig(ctx, input.ConfigKey)
	if err != nil {
		return nil, err // propagates repository.ErrNotFound as-is
	}
	if err := requireTenantMatchPtr(actor, existing.OrganizationID); err != nil {
		return nil, err
	}

	saved, err := s.repo.SaveConfig(ctx, input)
	if err != nil {
		return nil, err
	}
	s.auditor.RecordConfigChange(ctx, AuditEvent{
		Action: ActionUpdate, Actor: actor, ConfigKey: input.ConfigKey,
		OldValue: existing.ConfigValue, NewValue: input.ConfigValue,
	})
	return saved, nil
}

// Delete removes a configuration entry by key.
func (s *Service) Delete(ctx context.Context, actor Actor, key string) error {
	if err := s.authorize(ctx, actor, ActionDelete, key); err != nil {
		return err
	}

	existing, err := s.repo.GetConfig(ctx, key)
	if err != nil {
		return err
	}
	if err := requireTenantMatchPtr(actor, existing.OrganizationID); err != nil {
		return err
	}

	if err := s.repo.DeleteConfig(ctx, key); err != nil {
		return err
	}
	s.auditor.RecordConfigChange(ctx, AuditEvent{
		Action: ActionDelete, Actor: actor, ConfigKey: key,
		OldValue: existing.ConfigValue,
	})
	return nil
}

// List retrieves configuration entries matching the given filter, scoped
// to the actor's own organization regardless of what filter.OrganizationID
// says — this is what makes List tenant-isolated rather than trusting
// caller-supplied input.
func (s *Service) List(ctx context.Context, actor Actor, filter repository.ListFilter) ([]repository.Configuration, error) {
	if err := s.authorize(ctx, actor, ActionRead, ""); err != nil {
		return nil, err
	}
	orgID := actor.OrganizationID
	filter.OrganizationID = &orgID
	return s.repo.ListConfigurations(ctx, filter)
}

// Versions returns the audit history for one configuration entry — this
// IS the versioning mechanism ("Add configuration versioning where
// required"), reusing configuration_history rather than a separate
// version-numbering system.
func (s *Service) Versions(ctx context.Context, actor Actor, configurationID string) ([]repository.ConfigurationHistory, error) {
	if err := s.authorize(ctx, actor, ActionRead, ""); err != nil {
		return nil, err
	}
	return s.repo.GetConfigurationHistory(ctx, configurationID)
}

func (s *Service) authorize(ctx context.Context, actor Actor, action Action, configKey string) error {
	allowed, err := s.authorizer.Authorize(ctx, actor, action, configKey)
	if err != nil {
		return err
	}
	if !allowed {
		return ErrUnauthorized
	}
	return nil
}

// requireTenantMatch enforces tenant isolation: the actor may only
// operate on configuration belonging to their own organization.
func requireTenantMatch(actor Actor, inputOrgID *string) error {
	if inputOrgID == nil || *inputOrgID != actor.OrganizationID {
		return ErrUnauthorized
	}
	return nil
}

func requireTenantMatchPtr(actor Actor, existingOrgID *string) error {
	return requireTenantMatch(actor, existingOrgID)
}
