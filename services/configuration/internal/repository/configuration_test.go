package repository

import (
	"context"
	"errors"
	"testing"
)

func TestSaveConfig_InsertsNewKey(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	saved, err := repo.SaveConfig(ctx, SaveConfigInput{
		ConfigKey:    "test_max_retries",
		ConfigValue:  "5",
		DataType:     DataTypeInt,
		Scope:        ScopeGlobal,
		IsEditable:   true,
		ChangeReason: "initial value",
	})
	if err != nil {
		t.Fatalf("expected insert to succeed, got error: %v", err)
	}
	if saved.ConfigValue != "5" {
		t.Fatalf("expected value 5, got %s", saved.ConfigValue)
	}

	got, err := repo.GetConfig(ctx, "test_max_retries")
	if err != nil {
		t.Fatalf("expected Get to succeed, got error: %v", err)
	}
	if got.ConfigValue != "5" {
		t.Fatalf("expected value 5, got %s", got.ConfigValue)
	}
}

func TestSaveConfig_UpdatesExistingKeyAndWritesHistory(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	first, err := repo.SaveConfig(ctx, SaveConfigInput{
		ConfigKey:   "test_timeout_seconds",
		ConfigValue: "30",
		DataType:    DataTypeInt,
		Scope:       ScopeGlobal,
	})
	if err != nil {
		t.Fatalf("expected first Save to succeed, got error: %v", err)
	}

	second, err := repo.SaveConfig(ctx, SaveConfigInput{
		ConfigKey:    "test_timeout_seconds",
		ConfigValue:  "60",
		DataType:     DataTypeInt,
		Scope:        ScopeGlobal,
		ChangeReason: "bumped timeout",
	})
	if err != nil {
		t.Fatalf("expected second Save (update) to succeed, got error: %v", err)
	}
	if second.ID != first.ID {
		t.Fatalf("expected upsert to keep the same row ID, got %s vs %s", first.ID, second.ID)
	}
	if second.ConfigValue != "60" {
		t.Fatalf("expected updated value 60, got %s", second.ConfigValue)
	}

	history, err := repo.GetConfigurationHistory(ctx, second.ID)
	if err != nil {
		t.Fatalf("expected history fetch to succeed, got error: %v", err)
	}
	if len(history) != 2 {
		t.Fatalf("expected 2 history rows (insert + update), got %d", len(history))
	}
	if history[0].NewValue != "60" {
		t.Fatalf("expected most recent history entry to be 60, got %s", history[0].NewValue)
	}
}

func TestGetConfig_NotFound(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	_, err := repo.GetConfig(ctx, "does-not-exist-key")
	if !errors.Is(err, ErrNotFound) {
		t.Fatalf("expected ErrNotFound, got: %v", err)
	}
}

func TestListConfigurations_FiltersByScope(t *testing.T) {
	repo := newTestPostgresRepository(t)
	ctx := context.Background()

	orgID := "11111111-1111-1111-1111-111111111111"

	_, err := repo.SaveConfig(ctx, SaveConfigInput{
		ConfigKey: "test_global_setting", ConfigValue: "x",
		DataType: DataTypeString, Scope: ScopeGlobal,
	})
	if err != nil {
		t.Fatalf("failed to seed global config: %v", err)
	}
	_, err = repo.SaveConfig(ctx, SaveConfigInput{
		ConfigKey: "test_org_setting", ConfigValue: "y",
		DataType: DataTypeString, Scope: ScopeOrganization, OrganizationID: &orgID,
	})
	if err != nil {
		t.Fatalf("failed to seed org config: %v", err)
	}

	orgResults, err := repo.ListConfigurations(ctx, ListFilter{Scope: ScopeOrganization})
	if err != nil {
		t.Fatalf("expected List to succeed, got error: %v", err)
	}
	for _, c := range orgResults {
		if c.Scope != ScopeOrganization {
			t.Fatalf("expected only ORGANIZATION-scoped rows, got scope %s for key %s", c.Scope, c.ConfigKey)
		}
	}
}
