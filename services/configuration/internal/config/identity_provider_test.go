package config

import (
	"strings"
	"testing"
)

// Test 1: OIDC missing issuer_url
func TestOIDCMissingIssuerURL(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oidc",
		ClientID:        "test",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "issuer_url") {
		t.Fatalf("Expected issuer_url error, got: %v", err)
	}
}

// Test 2: OIDC missing client_id
func TestOIDCMissingClientID(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oidc",
		IssuerURL:       "https://example.com",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "client_id") {
		t.Fatalf("Expected client_id error, got: %v", err)
	}
}

// Test 3: OIDC missing client_secret_ref
func TestOIDCMissingClientSecretRef(t *testing.T) {
	cfg := ProviderConfig{
		Type:      "oidc",
		IssuerURL: "https://example.com",
		ClientID:  "test",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "client_secret_ref") {
		t.Fatalf("Expected client_secret_ref error, got: %v", err)
	}
}

// Test 4: OIDC valid configuration
func TestOIDCValid(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oidc",
		IssuerURL:       "https://example.com",
		ClientID:        "test",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}
}

// Test 5: OAuth2 missing authorization_url
func TestOAuth2MissingAuthURL(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oauth2",
		TokenURL:        "https://example.com/token",
		ClientID:        "test",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "authorization_url") {
		t.Fatalf("Expected authorization_url error, got: %v", err)
	}
}

// Test 6: OAuth2 missing token_url
func TestOAuth2MissingTokenURL(t *testing.T) {
	cfg := ProviderConfig{
		Type:             "oauth2",
		AuthorizationURL: "https://example.com/auth",
		ClientID:         "test",
		ClientSecretRef:  "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "token_url") {
		t.Fatalf("Expected token_url error, got: %v", err)
	}
}

// Test 7: OAuth2 valid configuration
func TestOAuth2Valid(t *testing.T) {
	cfg := ProviderConfig{
		Type:             "oauth2",
		AuthorizationURL: "https://example.com/auth",
		TokenURL:         "https://example.com/token",
		ClientID:         "test",
		ClientSecretRef:  "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}
}

// Test 8: SAML missing entity_id
func TestSAMLMissingEntityID(t *testing.T) {
	cfg := ProviderConfig{
		Type:          "saml",
		SSOURL:        "https://example.com/sso",
		SigningKeyRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "entity_id") {
		t.Fatalf("Expected entity_id error, got: %v", err)
	}
}

// Test 9: SAML missing sso_url
func TestSAMLMissingSSOURL(t *testing.T) {
	cfg := ProviderConfig{
		Type:          "saml",
		EntityID:      "urn:example:sp",
		SigningKeyRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil || !strings.Contains(err.Error(), "sso_url") {
		t.Fatalf("Expected sso_url error, got: %v", err)
	}
}

// Test 10: SAML valid configuration
func TestSAMLValid(t *testing.T) {
	cfg := ProviderConfig{
		Type:          "saml",
		EntityID:      "urn:example:sp",
		SSOURL:        "https://example.com/sso",
		SigningKeyRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}
}

// Test 11: Invalid URL format
func TestInvalidURLFormat(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oidc",
		IssuerURL:       "not-a-url",
		ClientID:        "test",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil {
		t.Fatal("Expected URL validation error")
	}
}

// Test 12: URL missing scheme
func TestURLMissingScheme(t *testing.T) {
	cfg := ProviderConfig{
		Type:            "oidc",
		IssuerURL:       "example.com",
		ClientID:        "test",
		ClientSecretRef: "ref",
	}
	err := ValidateProviderConfig(cfg)
	if err == nil {
		t.Fatal("Expected URL scheme validation error")
	}
}
