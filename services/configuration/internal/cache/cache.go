// Package cache provides a small in-memory, TTL-based cache used to keep
// GET requests off Postgres. Swapping this for Redis later just means
// writing a new type that satisfies the Cache interface below — nothing
// in the repository layer needs to change.
package cache

import (
	"sync"
	"time"
)

// Cache is the contract the repository decorator depends on. Keeping it
// small and interface-based means the in-memory implementation here can
// later be swapped for a Redis-backed one without touching callers.
type Cache interface {
	Get(key string) (string, bool)
	Set(key string, value string, ttl time.Duration)
	Delete(key string)
}

type entry struct {
	value     string
	expiresAt time.Time
}

// InMemoryCache is a simple, goroutine-safe, TTL-based cache backed by a
// map. A background goroutine periodically sweeps expired entries so
// memory doesn't grow unbounded with stale keys.
type InMemoryCache struct {
	mu      sync.RWMutex
	entries map[string]entry
	stopCh  chan struct{}
}

// NewInMemoryCache creates a cache and starts its background janitor,
// which wakes up every `sweepInterval` to evict expired entries. Call
// Close() when done to stop the janitor goroutine. Pass 0 to disable
// the janitor (useful in tests).
func NewInMemoryCache(sweepInterval time.Duration) *InMemoryCache {
	c := &InMemoryCache{
		entries: make(map[string]entry),
		stopCh:  make(chan struct{}),
	}

	if sweepInterval > 0 {
		go c.janitor(sweepInterval)
	}

	return c
}

func (c *InMemoryCache) Get(key string) (string, bool) {
	c.mu.RLock()
	e, ok := c.entries[key]
	c.mu.RUnlock()

	if !ok {
		return "", false
	}
	if time.Now().After(e.expiresAt) {
		// Expired but not yet swept — treat as a miss.
		return "", false
	}
	return e.value, true
}

func (c *InMemoryCache) Set(key string, value string, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.entries[key] = entry{
		value:     value,
		expiresAt: time.Now().Add(ttl),
	}
}

func (c *InMemoryCache) Delete(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.entries, key)
}

// Close stops the background janitor. Safe to call once.
func (c *InMemoryCache) Close() {
	close(c.stopCh)
}

func (c *InMemoryCache) janitor(interval time.Duration) {
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			c.evictExpired()
		case <-c.stopCh:
			return
		}
	}
}

func (c *InMemoryCache) evictExpired() {
	now := time.Now()
	c.mu.Lock()
	defer c.mu.Unlock()
	for k, e := range c.entries {
		if now.After(e.expiresAt) {
			delete(c.entries, k)
		}
	}
}
