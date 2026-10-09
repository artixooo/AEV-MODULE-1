package idpconfig

import (
	"context"
	"testing"
)

// These tests document the required-field validation behavior that
// Harshit's ValidateProviderConfig (adapted from
// internal/config/identity_provider_validation.go) is expected to
// enforce once wired into SaveIdentityProviderConfig. They are skipped
// for now since that validation isn't wired in yet — remove the
// t.Skip() calls once it is, and these should pass.

func TestSaveIdentityProviderConfig_RejectsOIDCMissingIssuerURL(t *testing.T) {

	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "66666666-6666-6666-6666-666666666666"

	incomplete := ProviderConfig{
		Type:            "oidc",
		Enabled:         true,
		ClientID:        "client-abc",
		ClientSecretRef: "secret://identity/" + orgID + "/client-secret",
		// IssuerURL intentionally omitted — required for OIDC per
		// docs/config_identity-provider.md, Section 10.
	}

	_, err := SaveIdentityProviderConfig(ctx, repo, orgID, incomplete)
	if err == nil {
		t.Fatal("expected an error for OIDC config missing issuer_url, got none")
	}
}

func TestSaveIdentityProviderConfig_RejectsOAuth2MissingTokenURL(t *testing.T) {

	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "77777777-7777-7777-7777-777777777777"

	incomplete := ProviderConfig{
		Type:             "oauth2",
		Enabled:          true,
		AuthorizationURL: "https://provider.example.com/authorize",
		ClientID:         "client-abc",
		ClientSecretRef:  "secret://identity/" + orgID + "/client-secret",
		// TokenURL intentionally omitted — required for OAuth2.
	}

	_, err := SaveIdentityProviderConfig(ctx, repo, orgID, incomplete)
	if err == nil {
		t.Fatal("expected an error for OAuth2 config missing token_url, got none")
	}
}

func TestSaveIdentityProviderConfig_RejectsSAMLMissingSigningKeyRef(t *testing.T) {

	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "88888888-8888-8888-8888-888888888888"

	incomplete := ProviderConfig{
		Type:     "saml",
		Enabled:  true,
		EntityID: "https://service.example.com/saml",
		SSOURL:   "https://idp.example.com/sso",
		// SigningKeyRef intentionally omitted — required for SAML.
	}

	_, err := SaveIdentityProviderConfig(ctx, repo, orgID, incomplete)
	if err == nil {
		t.Fatal("expected an error for SAML config missing signing_key_ref, got none")
	}
}

func TestSaveIdentityProviderConfig_RejectsInvalidURL(t *testing.T) {

	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "99999999-9999-9999-9999-999999999999"

	invalid := ProviderConfig{
		Type:            "oidc",
		Enabled:         true,
		IssuerURL:       "not-a-valid-url",
		ClientID:        "client-abc",
		ClientSecretRef: "secret://identity/" + orgID + "/client-secret",
	}

	_, err := SaveIdentityProviderConfig(ctx, repo, orgID, invalid)
	if err == nil {
		t.Fatal("expected an error for a malformed issuer_url, got none")
	}
}
