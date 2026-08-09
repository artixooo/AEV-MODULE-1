// Package db is the single place that knows how to open a connection to
// Postgres and assemble the configuration service's repository + cache
// layers. Nothing else in this service should call pgxpool directly —
// call db.New(ctx) once at startup and pass the returned Repository
// wherever it's needed (HTTP handlers, gRPC handlers, etc).
package db

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"configuration/internal/cache"
	"configuration/internal/repository"
)

// Config holds everything needed to open the connection and tune the
// cache in front of it. Zero values fall back to sensible defaults —
// see New().
type Config struct {
	// DatabaseURL is a full Postgres connection string, e.g.
	// "postgres://user:password@localhost:5432/configuration_db?sslmode=disable".
	// If empty, New() reads it from the DATABASE_URL environment variable.
	DatabaseURL string

	// CacheTTL is how long a cached config/flag value stays fresh before
	// being re-fetched from Postgres. Defaults to cache.DefaultTTL (30s)
	// if left at zero.
	CacheTTL time.Duration

	// CacheSweepInterval controls how often the in-memory cache's
	// background janitor sweeps out expired entries. Defaults to 1
	// minute if left at zero.
	CacheSweepInterval time.Duration
}

// Handle bundles the live connection pool with the ready-to-use
// repository, so callers can both do repository calls and cleanly shut
// the pool down when the service stops.
type Handle struct {
	Pool *pgxpool.Pool
	Repo repository.Repository
}

// New reads the connection config, opens a pgx connection pool against
// the tables created by database/migration/, and wires up the caching
// decorator on top of the Postgres repository.
//
// This does NOT create or alter any tables — it only connects to
// whatever schema already exists in the target database (the one
// created by the migrations under database/migration/ at the repo
// root). If those tables don't exist yet, calls through the returned
// Repository will fail with a Postgres "relation does not exist" error,
// not from anything in this package.
func New(ctx context.Context, cfg Config) (*Handle, error) {
	dsn := cfg.DatabaseURL
	if dsn == "" {
		dsn = os.Getenv("DATABASE_URL")
	}
	if dsn == "" {
		return nil, fmt.Errorf("db: no connection string provided (set Config.DatabaseURL or the DATABASE_URL env var)")
	}

	pool, err := pgxpool.New(ctx, dsn)
	if err != nil {
		return nil, fmt.Errorf("db: failed to create connection pool: %w", err)
	}

	// Fail fast at startup if the DB is unreachable, rather than only
	// discovering it on the first real request.
	if err := pool.Ping(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("db: failed to ping database: %w", err)
	}

	sweepInterval := cfg.CacheSweepInterval
	if sweepInterval <= 0 {
		sweepInterval = time.Minute
	}

	pgRepo := repository.NewPostgresRepository(pool)
	memCache := cache.NewInMemoryCache(sweepInterval)
	cachedRepo := cache.NewCachedRepository(pgRepo, memCache, cfg.CacheTTL) // 0 => cache.DefaultTTL

	return &Handle{
		Pool: pool,
		Repo: cachedRepo,
	}, nil
}

// Close releases the underlying connection pool. Call this once, on
// service shutdown (e.g. deferred right after db.New in main()).
func (h *Handle) Close() {
	h.Pool.Close()
}
