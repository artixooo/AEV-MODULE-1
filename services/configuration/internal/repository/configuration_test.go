package repository

import (
    "context"
    "errors"
    "fmt"
    "testing"
    "time"
)

// uniqueTestKey generates a config_key that cannot collide with real data
// or with other test runs (including parallel/concurrent ones), so tests
// never need to touch or delete anything that isn't theirs.
func uniqueTestKey(base string) string {
    return fmt.Sprintf("%s_%d", base, time.Now().UnixNano())
}

// cleanupTestConfig removes a test's own uniquely-generated row after the
// test finishes, just to keep the database tidy - not required for
// isolation, since the key is already unique.
func cleanupTestConfig(t *testing.T, repo *PostgresRepository, key string) {
    t.Helper()
    t.Cleanup(func() {
        _, _ = repo.db.Exec(context.Background(), `DELETE FROM configuration WHERE config_key = $1`, key)
    })
}

func TestSaveConfig_InsertsNewKey(t *testing.T) {
    repo := newTestPostgresRepository(t)
    ctx := context.Background()
    key := uniqueTestKey("test_max_retries")
    cleanupTestConfig(t, repo, key)

    saved, err := repo.SaveConfig(ctx, SaveConfigInput{
        ConfigKey:    key,
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

    got, err := repo.GetConfig(ctx, key)
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
    key := uniqueTestKey("test_timeout_seconds")
    cleanupTestConfig(t, repo, key)

    first, err := repo.SaveConfig(ctx, SaveConfigInput{
        ConfigKey:   key,
        ConfigValue: "30",
        DataType:    DataTypeInt,
        Scope:       ScopeGlobal,
    })
    if err != nil {
        t.Fatalf("expected first Save to succeed, got error: %v", err)
    }

    second, err := repo.SaveConfig(ctx, SaveConfigInput{
        ConfigKey:    key,
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
    globalKey := uniqueTestKey("test_global_setting")
    orgKey := uniqueTestKey("test_org_setting")
    cleanupTestConfig(t, repo, globalKey)
    cleanupTestConfig(t, repo, orgKey)

    orgID := "11111111-1111-1111-1111-111111111111"

    _, err := repo.SaveConfig(ctx, SaveConfigInput{
        ConfigKey: globalKey, ConfigValue: "x",
        DataType: DataTypeString, Scope: ScopeGlobal,
    })
    if err != nil {
        t.Fatalf("failed to seed global config: %v", err)
    }
    _, err = repo.SaveConfig(ctx, SaveConfigInput{
        ConfigKey: orgKey, ConfigValue: "y",
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
