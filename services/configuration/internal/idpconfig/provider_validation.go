// Package idpconfig — provider-specific validation, adapted from
// Harshit's internal/config/identity_provider_validation.go to operate
// on ProviderConfig instead of a map[string]interface{} metadata field.
package idpconfig

import (
	"errors"
	"fmt"
	"net/url"
	"strings"
)

var (
	ErrInvalidProviderType  = errors.New("invalid provider_type")
	ErrMissingRequiredField = errors.New("missing required field")
	ErrInvalidURL           = errors.New("invalid URL format")
)

// ValidateProviderConfig checks that cfg has all required fields for its
// declared Type, and that any URL fields are well-formed. Called from
// SaveIdentityProviderConfig before persistence.
func ValidateProviderConfig(cfg ProviderConfig) error {
	switch cfg.Type {
	case "oidc":
		return validateOIDC(cfg)
	case "oauth2":
		return validateOAuth2(cfg)
	case "saml":
		return validateSAML(cfg)
	default:
		return fmt.Errorf("%w: %q", ErrInvalidProviderType, cfg.Type)
	}
}

func validateOIDC(cfg ProviderConfig) error {
	if err := requireNonEmpty("issuer_url", cfg.IssuerURL); err != nil {
		return err
	}
	if err := requireNonEmpty("client_id", cfg.ClientID); err != nil {
		return err
	}
	if err := requireNonEmpty("client_secret_ref", cfg.ClientSecretRef); err != nil {
		return err
	}

	if err := validateURL(cfg.IssuerURL); err != nil {
		return fmt.Errorf("invalid issuer_url: %w", err)
	}
	if cfg.TokenURL != "" {
		if err := validateURL(cfg.TokenURL); err != nil {
			return fmt.Errorf("invalid token_url: %w", err)
		}
	}
	if cfg.UserinfoURL != "" {
		if err := validateURL(cfg.UserinfoURL); err != nil {
			return fmt.Errorf("invalid userinfo_url: %w", err)
		}
	}
	if cfg.AuthorizationURL != "" {
		if err := validateURL(cfg.AuthorizationURL); err != nil {
			return fmt.Errorf("invalid authorization_url: %w", err)
		}
	}
	return nil
}

func validateOAuth2(cfg ProviderConfig) error {
	if err := requireNonEmpty("authorization_url", cfg.AuthorizationURL); err != nil {
		return err
	}
	if err := requireNonEmpty("token_url", cfg.TokenURL); err != nil {
		return err
	}
	if err := requireNonEmpty("client_id", cfg.ClientID); err != nil {
		return err
	}
	if err := requireNonEmpty("client_secret_ref", cfg.ClientSecretRef); err != nil {
		return err
	}

	if err := validateURL(cfg.AuthorizationURL); err != nil {
		return fmt.Errorf("invalid authorization_url: %w", err)
	}
	if err := validateURL(cfg.TokenURL); err != nil {
		return fmt.Errorf("invalid token_url: %w", err)
	}
	return nil
}

func validateSAML(cfg ProviderConfig) error {
	if err := requireNonEmpty("entity_id", cfg.EntityID); err != nil {
		return err
	}
	if err := requireNonEmpty("sso_url", cfg.SSOURL); err != nil {
		return err
	}
	if err := requireNonEmpty("signing_key_ref", cfg.SigningKeyRef); err != nil {
		return err
	}

	if err := validateURL(cfg.SSOURL); err != nil {
		return fmt.Errorf("invalid sso_url: %w", err)
	}
	if cfg.MetadataURL != "" {
		if err := validateURL(cfg.MetadataURL); err != nil {
			return fmt.Errorf("invalid metadata_url: %w", err)
		}
	}
	return nil
}

func requireNonEmpty(fieldName, value string) error {
	if strings.TrimSpace(value) == "" {
		return fmt.Errorf("%w: %s is required for this provider type", ErrMissingRequiredField, fieldName)
	}
	return nil
}

func validateURL(urlStr string) error {
	if strings.TrimSpace(urlStr) == "" {
		return ErrInvalidURL
	}
	parsed, err := url.Parse(urlStr)
	if err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidURL, err)
	}
	if parsed.Scheme == "" || parsed.Host == "" {
		return ErrInvalidURL
	}
	if parsed.Scheme != "https" && parsed.Scheme != "http" {
		return fmt.Errorf("%w: URL must use http or https scheme", ErrInvalidURL)
	}
	return nil
}
