package cache

import (
	"testing"
	"time"
)

func TestInMemoryCache_SetGetDelete(t *testing.T) {
	c := NewInMemoryCache(0) // no janitor needed for this test
	defer c.Close()

	if _, ok := c.Get("missing"); ok {
		t.Fatal("expected miss for a key that was never set")
	}

	c.Set("greeting", "hello", time.Minute)
	v, ok := c.Get("greeting")
	if !ok || v != "hello" {
		t.Fatalf("expected hit with value %q, got (%q, %v)", "hello", v, ok)
	}

	c.Delete("greeting")
	if _, ok := c.Get("greeting"); ok {
		t.Fatal("expected miss after Delete")
	}
}

func TestInMemoryCache_TTLExpiry(t *testing.T) {
	c := NewInMemoryCache(0)
	defer c.Close()

	c.Set("short-lived", "value", 10*time.Millisecond)

	if v, ok := c.Get("short-lived"); !ok || v != "value" {
		t.Fatalf("expected immediate hit, got (%q, %v)", v, ok)
	}

	time.Sleep(30 * time.Millisecond)

	if _, ok := c.Get("short-lived"); ok {
		t.Fatal("expected miss after TTL expiry")
	}
}

func TestInMemoryCache_JanitorSweepsExpiredEntries(t *testing.T) {
	c := NewInMemoryCache(10 * time.Millisecond)
	defer c.Close()

	c.Set("key", "value", 5*time.Millisecond)
	time.Sleep(40 * time.Millisecond) // let the janitor run at least once

	c.mu.RLock()
	_, stillPresent := c.entries["key"]
	c.mu.RUnlock()

	if stillPresent {
		t.Fatal("expected janitor to have evicted the expired entry from the map")
	}
}
