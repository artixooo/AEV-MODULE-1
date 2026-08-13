package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

func getPort() string {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}
	return port
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, `{"status":"ok","service":"audit"}`)
}

func main() {
	port := getPort()

	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)

	server := &http.Server{
		Addr:    ":" + port,
		Handler: mux,
	}

	log.Printf("Audit Service starting on port %s", port)

	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server failed: %v", err)
	}
}