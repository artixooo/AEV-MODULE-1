package db

import (
	"context"
	"os"
	"strings"
	"testing"
	"time"

	"configuration/internal/repository"
)

func TestNew_FailsWithoutConnectionString(t *testing.T) {
	// Guard against a real DATABASE_URL leaking into this test from the
	// environment the test runner happens to be executed in.
	t.Setenv("DATABASE_URL", "")

	_, err := New(context.Background(), Config{})
	if err == nil {
		t.Fatal("expected an error when no DatabaseURL is set and DATABASE_URL is empty")
	}
	if !strings.Contains(err.Error(), "no connection string provided") {
		t.Fatalf("expected a clear 'no connection string' error, got: %v", err)
	}
}

func TestNew_ReadsConnectionStringFromEnv(t *testing.T) {
	// Point at something syntactically valid but unreachable so we
	// exercise the "read from env" path without needing a real DB.
	// Loopback + an unused port fails fast with "connection refused"
	// rather than hanging, which is exactly the fail-fast behavior this
	// package is supposed to guarantee.
	t.Setenv("DATABASE_URL", "postgres://user:pass@127.0.0.1:5999/pod_alpha?sslmode=disable")

	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	_, err := New(ctx, Config{ConnectTimeout: 1 * time.Second})
	if err == nil {
		t.Fatal("expected an error connecting to an unreachable database")
	}
	if !strings.Contains(err.Error(), "db: failed to reach database") {
		t.Fatalf("expected a 'failed to reach database' error, got: %v", err)
	}
}

func TestNew_FailsFastOnUnreachableDatabase(t *testing.T) {
	// The core requirement from the task: an unreachable DB must fail
	// fast, not hang. We bound ConnectTimeout tightly and assert New()
	// returns well within a generous outer deadline.
	start := time.Now()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err := New(ctx, Config{
		DatabaseURL:    "postgres://user:pass@127.0.0.1:5999/pod_alpha?sslmode=disable",
		ConnectTimeout: 500 * time.Millisecond,
	})

	elapsed := time.Since(start)

	if err == nil {
		t.Fatal("expected an error connecting to an unreachable database")
	}
	if elapsed > 2*time.Second {
		t.Fatalf("New() took %s to fail — expected it to fail fast (well under its ConnectTimeout budget), not hang", elapsed)
	}
}

func TestNew_RejectsMalformedDSN(t *testing.T) {
	_, err := New(context.Background(), Config{
		DatabaseURL: "not-a-valid-connection-string",
	})
	if err == nil {
		t.Fatal("expected an error for a malformed DSN")
	}
}

// TestNew_LiveConnection is an opt-in integration test: it only runs if
// TEST_DATABASE_URL is set to a real, reachable pod_alpha connection
// string (e.g. in CI, or locally against your dev database). It proves
// the repository + cache layers work end-to-end against the real
// database, not just that New() handles error cases correctly.
//
// Run it explicitly with:
//
//	$env:TEST_DATABASE_URL = "postgres://user:pass@host:5432/pod_alpha?sslmode=disable"
//	go test ./internal/db/... -run TestNew_LiveConnection -v
func TestNew_LiveConnection(t *testing.T) {
	dsn := os.Getenv("TEST_DATABASE_URL")
	if dsn == "" {
		t.Skip("TEST_DATABASE_URL not set — skipping live connectivity test")
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	handle, err := New(ctx, Config{DatabaseURL: dsn})
	if err != nil {
		t.Fatalf("expected a successful connection to %s, got: %v", dsn, err)
	}
	defer handle.Close()

	// End-to-end proof: the repository can actually query the approved
	// schema's tables through the cache decorator.
	configs, err := handle.Repo.ListConfigurations(ctx, repository.ListFilter{})
	if err != nil {
		t.Fatalf("expected ListConfigurations to succeed against the live DB, got: %v", err)
	}
	t.Logf("connected successfully — found %d row(s) in `configuration`", len(configs))

	flags, err := handle.Repo.ListFeatureFlags(ctx, repository.ListFilter{})
	if err != nil {
		t.Fatalf("expected ListFeatureFlags to succeed against the live DB, got: %v", err)
	}
	t.Logf("found %d row(s) in `feature_flags`", len(flags))
}
