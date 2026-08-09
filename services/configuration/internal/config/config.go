package config

import (
	"log"
	"os"
)

// Config holds all environment-based settings for the Configuration Service.
type Config struct {
	Port string
}

// Load reads environment variables and returns a populated Config.
// If a variable isn't set, it falls back to a sensible default.
func Load() *Config {
	cfg := &Config{
		Port: getEnv("PORT", "8082"),
	}

	log.Printf("Loaded configuration: Port=%s", cfg.Port)
	return cfg
}

// getEnv returns the value of an environment variable, or a default if unset.
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}
