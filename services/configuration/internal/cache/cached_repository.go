package cache

import (
	"context"
	"encoding/json"
	"time"

	"configuration/internal/repository"
)

// DefaultTTL is how long a cached entry stays fresh before it's
// considered stale and re-fetched from Postgres.
const DefaultTTL = 30 * time.Second

// CachedRepository wraps a repository.Repository and serves single-item
// reads (GetConfig, GetFeatureFlag) from a cache first, falling back to
// Postgres on a miss. Writes go to Postgres first, then write through to
// the cache so a read immediately after a save is never stale.
//
// List queries and history reads are intentionally NOT cached:
//   - ListConfigurations / ListFeatureFlags take arbitrary filters, so
//     there's no single stable cache key per call worth reusing.
//   - GetConfigurationHistory is an audit trail; it should always reflect
//     the latest state rather than a cached snapshot.
type CachedRepository struct {
	repo repository.Repository
	c    Cache
	ttl  time.Duration
}

// NewCachedRepository builds a caching decorator around an existing
// Repository. If ttl is 0, DefaultTTL is used.
func NewCachedRepository(repo repository.Repository, c Cache, ttl time.Duration) *CachedRepository {
	if ttl <= 0 {
		ttl = DefaultTTL
	}
	return &CachedRepository{repo: repo, c: c, ttl: ttl}
}

var _ repository.Repository = (*CachedRepository)(nil) // compile-time interface check

func configCacheKey(key string) string { return "config:" + key }
func flagCacheKey(key string) string   { return "flag:" + key }

// ---- Configuration ---------------------------------------------------------

func (c *CachedRepository) GetConfig(ctx context.Context, key string) (*repository.Configuration, error) {
	cacheKey := configCacheKey(key)

	if raw, ok := c.c.Get(cacheKey); ok {
		var cfg repository.Configuration
		if err := json.Unmarshal([]byte(raw), &cfg); err == nil {
			return &cfg, nil
		}
		// Corrupt cache entry — fall through and re-fetch from Postgres.
	}

	cfg, err := c.repo.GetConfig(ctx, key)
	if err != nil {
		return nil, err
	}

	if raw, err := json.Marshal(cfg); err == nil {
		c.c.Set(cacheKey, string(raw), c.ttl)
	}
	return cfg, nil
}

func (c *CachedRepository) SaveConfig(ctx context.Context, input repository.SaveConfigInput) (*repository.Configuration, error) {
	saved, err := c.repo.SaveConfig(ctx, input)
	if err != nil {
		return nil, err
	}

	if raw, err := json.Marshal(saved); err == nil {
		c.c.Set(configCacheKey(input.ConfigKey), string(raw), c.ttl)
	}
	return saved, nil
}

func (c *CachedRepository) ListConfigurations(ctx context.Context, filter repository.ListFilter) ([]repository.Configuration, error) {
	return c.repo.ListConfigurations(ctx, filter) // not cached, see type doc
}

func (c *CachedRepository) GetConfigurationHistory(ctx context.Context, configurationID string) ([]repository.ConfigurationHistory, error) {
	return c.repo.GetConfigurationHistory(ctx, configurationID) // not cached, see type doc
}

// ---- Feature flags ----------------------------------------------------------

func (c *CachedRepository) GetFeatureFlag(ctx context.Context, flagKey string) (*repository.FeatureFlag, error) {
	cacheKey := flagCacheKey(flagKey)

	if raw, ok := c.c.Get(cacheKey); ok {
		var f repository.FeatureFlag
		if err := json.Unmarshal([]byte(raw), &f); err == nil {
			return &f, nil
		}
	}

	f, err := c.repo.GetFeatureFlag(ctx, flagKey)
	if err != nil {
		return nil, err
	}

	if raw, err := json.Marshal(f); err == nil {
		c.c.Set(cacheKey, string(raw), c.ttl)
	}
	return f, nil
}

func (c *CachedRepository) SaveFeatureFlag(ctx context.Context, input repository.SaveFeatureFlagInput) (*repository.FeatureFlag, error) {
	saved, err := c.repo.SaveFeatureFlag(ctx, input)
	if err != nil {
		return nil, err
	}

	if raw, err := json.Marshal(saved); err == nil {
		c.c.Set(flagCacheKey(input.FlagKey), string(raw), c.ttl)
	}
	return saved, nil
}

func (c *CachedRepository) ListFeatureFlags(ctx context.Context, filter repository.ListFilter) ([]repository.FeatureFlag, error) {
	return c.repo.ListFeatureFlags(ctx, filter) // not cached, see type doc
}

// InvalidateConfig / InvalidateFlag force the next read to hit Postgres —
// useful if the row was changed out-of-band (e.g. a direct DB edit or a
// migration/backfill) rather than through this repository.
func (c *CachedRepository) InvalidateConfig(key string) { c.c.Delete(configCacheKey(key)) }
func (c *CachedRepository) InvalidateFlag(key string)   { c.c.Delete(flagCacheKey(key)) }

func (c *CachedRepository) DeleteConfig(ctx context.Context, key string) error {
	if err := c.repo.DeleteConfig(ctx, key); err != nil {
		return err
	}
	c.c.Delete(configCacheKey(key))
	return nil
}
