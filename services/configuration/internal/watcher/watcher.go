package watcher

import (
	"log"
	"time"
)

// Watcher periodically checks for configuration changes.
type Watcher struct {
	Interval time.Duration
}

// NewWatcher creates a Watcher that checks every `interval`.
func NewWatcher(interval time.Duration) *Watcher {
	return &Watcher{Interval: interval}
}

// Start begins the watch loop. This runs forever until the program stops.
func (w *Watcher) Start() {
	ticker := time.NewTicker(w.Interval)
	go func() {
		for range ticker.C {
			w.checkForChanges()
		}
	}()
	log.Printf("Watcher started, checking every %s", w.Interval)
}

// checkForChanges will eventually query the repository layer for updates.
// For now, it just logs — real logic gets added once the repository layer exists.
func (w *Watcher) checkForChanges() {
	log.Println("Watcher: checking for configuration changes...")
}
