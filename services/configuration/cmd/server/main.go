package main

import (
	"fmt"
	"log"
	"net/http"
	"time"

	"configuration/internal/config"
	"configuration/internal/watcher"
)

func main() {
	cfg := config.Load()
	w := watcher.NewWatcher(05 * time.Second)
	w.Start()

	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Configuration Service is healthy")
	})

	log.Printf("Config Service starting on port %s...", cfg.Port)
	if err := http.ListenAndServe(":"+cfg.Port, nil); err != nil {
		log.Fatal(err)
	}
}
