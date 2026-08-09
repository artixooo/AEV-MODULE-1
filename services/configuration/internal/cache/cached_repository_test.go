package cache

import (
	"context"
	"testing"
	"time"

	"configuration/internal/repository"
)

func TestCachedRepository_GetConfig_ServesSecondCallFromCache(t *testing.T) {
	fake := newFakeRepository()
	fake.configs["max_upload_mb"] = &repository.Configuration{
		ID: "id-1", ConfigKey: "max_upload_mb", ConfigValue: "50",
	}

	repo := NewCachedRepository(fake, NewInMemoryCache(0), time.Minute)
	ctx := context.Background()

	if _, err := repo.GetConfig(ctx, "max_upload_mb"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err := repo.GetConfig(ctx, "max_upload_mb"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if fake.getConfigN != 1 {
		t.Fatalf("expected exactly 1 underlying GetConfig call (2nd should hit cache), got %d", fake.getConfigN)
	}
}

func TestCachedRepository_SaveConfig_WriteThroughAvoidsExtraDBHit(t *testing.T) {
	fake := newFakeRepository()
	repo := NewCachedRepository(fake, NewInMemoryCache(0), time.Minute)
	ctx := context.Background()

	_, err := repo.SaveConfig(ctx, repository.SaveConfigInput{
		ConfigKey:   "feature_x_timeout",
		ConfigValue: "30s",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	cfg, err := repo.GetConfig(ctx, "feature_x_timeout")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.ConfigValue != "30s" {
		t.Fatalf("expected value %q, got %q", "30s", cfg.ConfigValue)
	}

	if fake.getConfigN != 0 {
		t.Fatalf("expected GetConfig to be served entirely from the write-through cache, but repo.GetConfig was called %d time(s)", fake.getConfigN)
	}
	if fake.saveConfigN != 1 {
		t.Fatalf("expected exactly 1 underlying SaveConfig call, got %d", fake.saveConfigN)
	}
}

func TestCachedRepository_GetFeatureFlag_ServesSecondCallFromCache(t *testing.T) {
	fake := newFakeRepository()
	fake.flags["new_checkout"] = &repository.FeatureFlag{
		ID: "id-1", FlagKey: "new_checkout", IsEnabled: true, RolloutPercentage: 100,
	}

	repo := NewCachedRepository(fake, NewInMemoryCache(0), time.Minute)
	ctx := context.Background()

	if _, err := repo.GetFeatureFlag(ctx, "new_checkout"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err := repo.GetFeatureFlag(ctx, "new_checkout"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if fake.getFlagN != 1 {
		t.Fatalf("expected exactly 1 underlying GetFeatureFlag call, got %d", fake.getFlagN)
	}
}

func TestCachedRepository_InvalidateConfig_ForcesRefetch(t *testing.T) {
	fake := newFakeRepository()
	fake.configs["region"] = &repository.Configuration{ID: "id-1", ConfigKey: "region", ConfigValue: "us-east-1"}

	repo := NewCachedRepository(fake, NewInMemoryCache(0), time.Minute)
	ctx := context.Background()

	if _, err := repo.GetConfig(ctx, "region"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	repo.InvalidateConfig("region")

	// Simulate the value changing out-of-band, then confirm the next read
	// goes back to the (fake) DB instead of serving the stale cached copy.
	fake.configs["region"].ConfigValue = "eu-west-1"

	cfg, err := repo.GetConfig(ctx, "region")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.ConfigValue != "eu-west-1" {
		t.Fatalf("expected fresh value %q after invalidation, got %q", "eu-west-1", cfg.ConfigValue)
	}
	if fake.getConfigN != 2 {
		t.Fatalf("expected invalidation to force a 2nd underlying call, got %d", fake.getConfigN)
	}
}

func TestCachedRepository_ListConfigurations_NotCached(t *testing.T) {
	fake := newFakeRepository()
	fake.configs["a"] = &repository.Configuration{ID: "1", ConfigKey: "a", ConfigValue: "1"}

	repo := NewCachedRepository(fake, NewInMemoryCache(0), time.Minute)
	ctx := context.Background()

	if _, err := repo.ListConfigurations(ctx, repository.ListFilter{}); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if _, err := repo.ListConfigurations(ctx, repository.ListFilter{}); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if fake.listConfigsN != 2 {
		t.Fatalf("expected list calls to always pass through (not cached), got %d underlying calls", fake.listConfigsN)
	}
}
