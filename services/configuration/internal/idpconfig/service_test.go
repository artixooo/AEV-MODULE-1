package idpconfig

import (
	"context"
	"os"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"configuration/internal/repository"
)

func newTestRepository(t *testing.T) repository.Repository {
	t.Helper()
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		t.Skip("DATABASE_URL not set, skipping idpconfig tests")
	}
	pool, err := pgxpool.New(context.Background(), dsn)
	if err != nil {
		t.Fatalf("failed to create pgx pool: %v", err)
	}
	t.Cleanup(func() {
		pool.Close()
	})
	return repository.NewPostgresRepository(pool)
}

func TestSaveAndGetIdentityProviderConfig_RoundTrips(t *testing.T) {
	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "11111111-1111-1111-1111-111111111111"

	input := ProviderConfig{
		Type:            "oidc",
		Enabled:         true,
		IssuerURL:       "https://identity.example.com",
		ClientID:        "client-abc",
		ClientSecretRef: "secret://identity/" + orgID + "/client-secret",
		Scopes:          []string{"openid", "profile"},
	}

	if _, err := SaveIdentityProviderConfig(ctx, repo, orgID, input); err != nil {
		t.Fatalf("expected Save to succeed, got error: %v", err)
	}

	got, err := GetIdentityProviderConfig(ctx, repo, orgID)
	if err != nil {
		t.Fatalf("expected Get to succeed, got error: %v", err)
	}
	if got.IssuerURL != input.IssuerURL {
		t.Fatalf("expected issuer_url %q, got %q", input.IssuerURL, got.IssuerURL)
	}
	if got.ClientSecretRef != input.ClientSecretRef {
		t.Fatalf("expected client_secret_ref %q, got %q", input.ClientSecretRef, got.ClientSecretRef)
	}
}

func TestGetIdentityProviderConfig_NotFoundForUnknownOrg(t *testing.T) {
	repo := newTestRepository(t)
	ctx := context.Background()

	_, err := GetIdentityProviderConfig(ctx, repo, "22222222-2222-2222-2222-222222222222")
	if err != repository.ErrNotFound {
		t.Fatalf("expected ErrNotFound, got: %v", err)
	}
}

func TestCrossTenantIsolation_OrgsCannotSeeEachOthersConfig(t *testing.T) {
	repo := newTestRepository(t)
	ctx := context.Background()

	orgA := "33333333-3333-3333-3333-333333333333"
	orgB := "44444444-4444-4444-4444-444444444444"

	configA := ProviderConfig{Type: "oidc", Enabled: true, IssuerURL: "https://company-a.example.com", ClientID: "client-a", ClientSecretRef: "secret://identity/org-a/client-secret"}
	configB := ProviderConfig{Type: "saml", Enabled: true, EntityID: "https://company-b.example.com/saml", SSOURL: "https://company-b.example.com/sso", SigningKeyRef: "secret://identity/org-b/signing-key"}

	if _, err := SaveIdentityProviderConfig(ctx, repo, orgA, configA); err != nil {
		t.Fatalf("failed to seed org A config: %v", err)
	}
	if _, err := SaveIdentityProviderConfig(ctx, repo, orgB, configB); err != nil {
		t.Fatalf("failed to seed org B config: %v", err)
	}

	gotA, err := GetIdentityProviderConfig(ctx, repo, orgA)
	if err != nil {
		t.Fatalf("expected org A to retrieve its own config, got error: %v", err)
	}
	if gotA.IssuerURL != configA.IssuerURL {
		t.Fatalf("org A got the wrong config: expected issuer %q, got %q", configA.IssuerURL, gotA.IssuerURL)
	}
	if gotA.Type == configB.Type {
		t.Fatalf("org A's config matches org B's type (%q) — possible cross-tenant leak", configB.Type)
	}

	gotB, err := GetIdentityProviderConfig(ctx, repo, orgB)
	if err != nil {
		t.Fatalf("expected org B to retrieve its own config, got error: %v", err)
	}
	if gotB.IssuerURL != configB.IssuerURL {
		t.Fatalf("org B got the wrong config: expected issuer %q, got %q", configB.IssuerURL, gotB.IssuerURL)
	}
}

func TestSaveIdentityProviderConfig_RejectsRawSecretIfInjected(t *testing.T) {
	repo := newTestRepository(t)
	ctx := context.Background()
	orgID := "55555555-5555-5555-5555-555555555555"

	validConfig := ProviderConfig{Type: "oidc", Enabled: true, IssuerURL: "https://identity.example.com", ClientID: "client-abc", ClientSecretRef: "secret://identity/" + orgID + "/ref"}
	if _, err := SaveIdentityProviderConfig(ctx, repo, orgID, validConfig); err != nil {
		t.Fatalf("expected a well-formed config with only *_ref fields to be accepted, got: %v", err)
	}
}
