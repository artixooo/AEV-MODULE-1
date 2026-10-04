package cache

import (
	"context"

	"configuration/internal/repository"
)

// fakeRepository is a minimal in-memory stand-in for repository.Repository,
// used only to test CachedRepository's caching behavior in isolation from
// Postgres. It tracks call counts so tests can assert whether a request
// was served from the cache or had to fall through.
type fakeRepository struct {
	configs       map[string]*repository.Configuration
	flags         map[string]*repository.FeatureFlag
	getConfigN    int
	saveConfigN   int
	deleteConfigN int
	getFlagN      int
	saveFlagN     int
	listConfigsN  int
	listFlagsN    int
	historyN      int
}

func newFakeRepository() *fakeRepository {
	return &fakeRepository{
		configs: make(map[string]*repository.Configuration),
		flags:   make(map[string]*repository.FeatureFlag),
	}
}

var _ repository.Repository = (*fakeRepository)(nil)

func (f *fakeRepository) GetConfig(ctx context.Context, key string) (*repository.Configuration, error) {
	f.getConfigN++
	c, ok := f.configs[key]
	if !ok {
		return nil, repository.ErrNotFound
	}
	cp := *c
	return &cp, nil
}

func (f *fakeRepository) SaveConfig(ctx context.Context, input repository.SaveConfigInput) (*repository.Configuration, error) {
	f.saveConfigN++
	c := &repository.Configuration{
		ID:          "fake-id-" + input.ConfigKey,
		ConfigKey:   input.ConfigKey,
		ConfigValue: input.ConfigValue,
		DataType:    input.DataType,
		Scope:       input.Scope,
		Description: input.Description,
		IsEditable:  input.IsEditable,
	}
	f.configs[input.ConfigKey] = c
	cp := *c
	return &cp, nil
}

func (f *fakeRepository) ListConfigurations(ctx context.Context, filter repository.ListFilter) ([]repository.Configuration, error) {
	f.listConfigsN++
	var out []repository.Configuration
	for _, c := range f.configs {
		out = append(out, *c)
	}
	return out, nil
}

func (f *fakeRepository) GetConfigurationHistory(ctx context.Context, configurationID string) ([]repository.ConfigurationHistory, error) {
	f.historyN++
	return nil, nil
}

func (f *fakeRepository) GetFeatureFlag(ctx context.Context, flagKey string) (*repository.FeatureFlag, error) {
	f.getFlagN++
	flag, ok := f.flags[flagKey]
	if !ok {
		return nil, repository.ErrNotFound
	}
	cp := *flag
	return &cp, nil
}

func (f *fakeRepository) SaveFeatureFlag(ctx context.Context, input repository.SaveFeatureFlagInput) (*repository.FeatureFlag, error) {
	f.saveFlagN++
	flag := &repository.FeatureFlag{
		ID:                "fake-id-" + input.FlagKey,
		FlagKey:           input.FlagKey,
		FlagName:          input.FlagName,
		Description:       input.Description,
		IsEnabled:         input.IsEnabled,
		Scope:             input.Scope,
		RolloutPercentage: input.RolloutPercentage,
	}
	f.flags[input.FlagKey] = flag
	cp := *flag
	return &cp, nil
}

func (f *fakeRepository) ListFeatureFlags(ctx context.Context, filter repository.ListFilter) ([]repository.FeatureFlag, error) {
	f.listFlagsN++
	var out []repository.FeatureFlag
	for _, flag := range f.flags {
		out = append(out, *flag)
	}
	return out, nil
}
func (f *fakeRepository) DeleteConfig(ctx context.Context, key string) error {
	f.deleteConfigN++
	if _, ok := f.configs[key]; !ok {
		return repository.ErrNotFound
	}
	delete(f.configs, key)
	return nil
}
