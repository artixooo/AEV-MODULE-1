// Command checkconn is a throwaway smoke test - not part of the
// service itself. Run it once after wiring up db.New to confirm:
//  1. Postgres is reachable with your DATABASE_URL
//  2. The approved tables (configuration, feature_flags,
//     configuration_history) actually exist and are queryable
//
// Usage (from services/configuration/):
//
//	$env:DATABASE_URL = "postgres://user:pass@host:5432/pod_alpha?sslmode=disable"
//	go run ./cmd/checkconn
package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"configuration/internal/db"
	"configuration/internal/repository"
)

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	fmt.Println("Step 1/4: opening connection + pinging Postgres...")
	handle, err := db.New(ctx, db.Config{})
	if err != nil {
		log.Fatalf("FAILED to connect: %v", err)
	}
	defer handle.Close()
	fmt.Println("  \u2713 connected and ping succeeded")

	fmt.Println("Step 2/4: querying `configuration` table (ListConfigurations)...")
	configs, err := handle.Repo.ListConfigurations(ctx, repository.ListFilter{})
	if err != nil {
		log.Fatalf("FAILED to query configuration table: %v", err)
	}
	fmt.Printf("  \u2713 query succeeded \u2014 found %d row(s) in `configuration`\n", len(configs))

	fmt.Println("Step 3/4: querying `feature_flags` table (ListFeatureFlags)...")
	flags, err := handle.Repo.ListFeatureFlags(ctx, repository.ListFilter{})
	if err != nil {
		log.Fatalf("FAILED to query feature_flags table: %v", err)
	}
	fmt.Printf("  \u2713 query succeeded \u2014 found %d row(s) in `feature_flags`\n", len(flags))

	fmt.Println("Step 4/4: querying `configuration_history` table...")
	var historyCount int
	err = handle.Pool.QueryRow(ctx, "SELECT COUNT(*) FROM configuration_history").Scan(&historyCount)
	if err != nil {
		log.Fatalf("FAILED to query configuration_history table: %v", err)
	}
	fmt.Printf("  \u2713 query succeeded \u2014 found %d row(s) in `configuration_history`\n", historyCount)

	fmt.Println("\nAll checks passed \u2014 the service is correctly connected to the database.")
}
