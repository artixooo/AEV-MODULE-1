package repository

import (
	"context"
	"errors"
	"testing"
)

// These tests only exercise the input-validation guard clauses that run
// before any database call, so they're safe to run against a repository
// with a nil pool. Full CRUD behavior (upserts, history writes, scope
// filtering) needs a real Postgres instance — see README for how to run
// those with a test database or testcontainers.

func TestSaveConfig_RejectsEmptyKey(t *testing.T) {
	repo := NewPostgresRepository(nil)

	_, err := repo.SaveConfig(context.Background(), SaveConfigInput{
		ConfigKey:   "",
		ConfigValue: "some-value",
	})

	if !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("expected ErrInvalidInput, got %v", err)
	}
}

func TestSaveFeatureFlag_RejectsEmptyKey(t *testing.T) {
	repo := NewPostgresRepository(nil)

	_, err := repo.SaveFeatureFlag(context.Background(), SaveFeatureFlagInput{
		FlagKey:  "",
		FlagName: "Some Flag",
	})

	if !errors.Is(err, ErrInvalidInput) {
		t.Fatalf("expected ErrInvalidInput, got %v", err)
	}
}

func TestScopeConstants_MatchApprovedSchema(t *testing.T) {
	// Guards against a typo silently breaking the CHECK-less but
	// convention-based scope column used by the approved schema.
	want := map[Scope]string{
		ScopeGlobal:       "GLOBAL",
		ScopeOrganization: "ORGANIZATION",
		ScopeWorkspace:    "WORKSPACE",
		ScopeProject:      "PROJECT",
	}
	for scope, str := range want {
		if string(scope) != str {
			t.Errorf("Scope %v should serialize to %q, got %q", scope, str, string(scope))
		}
	}
}
