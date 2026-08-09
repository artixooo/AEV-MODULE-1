package repository

import (
	"context"
	"testing"
)

func TestSaveFeatureFlag_InsertThenUpsertUpdatesInPlace(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	first, err := repo.SaveFeatureFlag(ctx, SaveFeatureFlagInput{
		FlagKey:           "test_new_checkout",
		FlagName:          "New Checkout Flow",
		IsEnabled:         false,
		Scope:             ScopeGlobal,
		RolloutPercentage: 0,
	})
	if err != nil {
		t.Fatalf("expected first Save to succeed, got error: %v", err)
	}

	second, err := repo.SaveFeatureFlag(ctx, SaveFeatureFlagInput{
		FlagKey:           "test_new_checkout",
		FlagName:          "New Checkout Flow",
		IsEnabled:         true,
		Scope:             ScopeGlobal,
		RolloutPercentage: 50,
	})
	if err != nil {
		t.Fatalf("expected upsert to succeed, got error: %v", err)
	}
	if second.ID != first.ID {
		t.Fatalf("expected ON CONFLICT to update the same row, got new ID %s vs %s", second.ID, first.ID)
	}
	if !second.IsEnabled || second.RolloutPercentage != 50 {
		t.Fatalf("expected updated flag to be enabled at 50%%, got enabled=%v rollout=%d", second.IsEnabled, second.RolloutPercentage)
	}
}

func TestGetFeatureFlag_NotFound(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	_, err := repo.GetFeatureFlag(ctx, "does-not-exist-flag")
	if err == nil {
		t.Fatal("expected an error for a missing flag")
	}
}
