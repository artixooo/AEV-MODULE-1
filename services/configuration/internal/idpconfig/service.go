package idpconfig

import (
	"context"
	"encoding/json"
	"fmt"

	"configuration/internal/repository"
	"configuration/internal/validation"
)

// ProviderConfig is the generic, extensible identity-provider settings
// shape stored as JSON inside the configuration table's config_value
// column. Fields are all optional at this level — provider-specific
// required-field validation happens separately (Task 2, Harshit).
type ProviderConfig struct {
	Type    string `json:"type"`
	Name    string `json:"name,omitempty"`
	Enabled bool   `json:"enabled"`

	// OIDC / OAuth2 fields
	IssuerURL        string   `json:"issuer_url,omitempty"`
	AuthorizationURL string   `json:"authorization_url,omitempty"`
	TokenURL         string   `json:"token_url,omitempty"`
	UserinfoURL      string   `json:"userinfo_url,omitempty"`
	JWKSURL          string   `json:"jwks_url,omitempty"`
	ClientID         string   `json:"client_id,omitempty"`
	ClientSecretRef  string   `json:"client_secret_ref,omitempty"`
	Scopes           []string `json:"scopes,omitempty"`

	// SAML fields
	EntityID      string `json:"entity_id,omitempty"`
	SSOURL        string `json:"sso_url,omitempty"`
	Certificate   string `json:"certificate,omitempty"`
	MetadataURL   string `json:"metadata_url,omitempty"`
	SigningKeyRef string `json:"signing_key_ref,omitempty"`
}

// asFieldMap converts a ProviderConfig into a flat field-name map, for
// checking against the sensitive-field list before persistence.
func (p ProviderConfig) asFieldMap() map[string]string {
	return map[string]string{
		"type":              p.Type,
		"issuer_url":        p.IssuerURL,
		"authorization_url": p.AuthorizationURL,
		"token_url":         p.TokenURL,
		"userinfo_url":      p.UserinfoURL,
		"jwks_url":          p.JWKSURL,
		"client_id":         p.ClientID,
		"client_secret_ref": p.ClientSecretRef,
		"entity_id":         p.EntityID,
		"sso_url":           p.SSOURL,
		"certificate":       p.Certificate,
		"metadata_url":      p.MetadataURL,
		"signing_key_ref":   p.SigningKeyRef,
	}
}

// SaveIdentityProviderConfig stores one organization's identity-provider
// configuration, scoped by organizationID, using the existing
// configuration table.
func SaveIdentityProviderConfig(ctx context.Context, repo repository.Repository, organizationID string, cfg ProviderConfig) (*repository.Configuration, error) {
	if err := ValidateProviderConfig(cfg); err != nil {
		return nil, err
	}
	if err := validation.ValidateNoSensitiveFields(cfg.asFieldMap()); err != nil {
		return nil, err
	}

	key, err := ConfigKeyForOrg(organizationID)
	if err != nil {
		return nil, err
	}

	valueJSON, err := json.Marshal(cfg)
	if err != nil {
		return nil, fmt.Errorf("idpconfig: failed to serialize provider config: %w", err)
	}

	orgID := organizationID
	return repo.SaveConfig(ctx, repository.SaveConfigInput{
		ConfigKey:      key,
		ConfigValue:    string(valueJSON),
		DataType:       repository.DataTypeJSON,
		Scope:          repository.ScopeOrganization,
		OrganizationID: &orgID,
		IsEditable:     true,
		ChangeReason:   "identity provider configuration update",
	})
}

// GetIdentityProviderConfig retrieves one organization's identity-provider
// configuration. Returns repository.ErrNotFound if none exists yet.
func GetIdentityProviderConfig(ctx context.Context, repo repository.Repository, organizationID string) (*ProviderConfig, error) {
	key, err := ConfigKeyForOrg(organizationID)
	if err != nil {
		return nil, err
	}

	stored, err := repo.GetConfig(ctx, key)
	if err != nil {
		return nil, err
	}

	if stored.OrganizationID == nil || *stored.OrganizationID != organizationID {
		return nil, repository.ErrNotFound
	}

	var cfg ProviderConfig
	if err := json.Unmarshal([]byte(stored.ConfigValue), &cfg); err != nil {
		return nil, fmt.Errorf("idpconfig: failed to parse stored provider config: %w", err)
	}
	return &cfg, nil
}
