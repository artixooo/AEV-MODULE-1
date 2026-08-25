package main

import (
	"log"
	"net/http"

	"audit/internal/config"
	"audit/internal/handlers"
	"audit/internal/repository"
)

func main() {
	cfg := config.Load()

	db, err := repository.ConnectDatabase(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("database connection failed: %v", err)
	}
	defer db.Close()

	mux := http.NewServeMux()
	mux.HandleFunc("/health", handlers.HealthHandler(db))

	server := &http.Server{
		Addr:    ":" + cfg.Port,
		Handler: mux,
	}

	log.Printf("Audit Service starting on port %s", cfg.Port)

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server failed: %v", err)
	}
}
