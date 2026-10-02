package config

import (
	"log"
	"os"
	"strconv"
)

// Config holds all environment-based settings for the Configuration Service.
type Config struct {
	Port                 string
	AuthEnabled          bool
	IdentityServiceURL   string
	JWTAlgorithm         string
	JWTExpirationSeconds int
}

// Load reads environment variables and returns a populated Config.
// If a variable isn't set, it falls back to a sensible default.
func Load() *Config {
	cfg := &Config{
		Port:                 getEnv("PORT", "8083"),
		AuthEnabled:          getEnvBool("AUTH_ENABLED", false),
		IdentityServiceURL:   getEnv("IDENTITY_SERVICE_URL", ""),
		JWTAlgorithm:         getEnv("JWT_ALGORITHM", "HS256"),
		JWTExpirationSeconds: getEnvInt("JWT_EXPIRATION", 3600),
	}

	log.Printf("Loaded configuration: Port=%s, AuthEnabled=%v, IdentityServiceURL=%s, JWTAlgorithm=%s, JWTExpirationSeconds=%d",
		cfg.Port, cfg.AuthEnabled, cfg.IdentityServiceURL, cfg.JWTAlgorithm, cfg.JWTExpirationSeconds)
	return cfg
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func getEnvBool(key string, defaultValue bool) bool {
	value, exists := os.LookupEnv(key)
	if !exists {
		return defaultValue
	}
	parsed, err := strconv.ParseBool(value)
	if err != nil {
		log.Printf("warning: invalid bool for %s=%q, using default %v", key, value, defaultValue)
		return defaultValue
	}
	return parsed
}

func getEnvInt(key string, defaultValue int) int {
	value, exists := os.LookupEnv(key)
	if !exists {
		return defaultValue
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		log.Printf("warning: invalid int for %s=%q, using default %d", key, value, defaultValue)
		return defaultValue
	}
	return parsed
}
