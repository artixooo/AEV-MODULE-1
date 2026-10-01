package config

import (
	"os"
	"testing"
)

func TestLoad_UsesDefaultsWhenEnvUnset(t *testing.T) {
	// Ensure a clean environment for this test.
	os.Unsetenv("PORT")
	os.Unsetenv("AUTH_ENABLED")
	os.Unsetenv("IDENTITY_SERVICE_URL")
	os.Unsetenv("JWT_ALGORITHM")
	os.Unsetenv("JWT_EXPIRATION")

	cfg := Load()

	if cfg.Port != "8083" {
		t.Errorf("expected default Port 8083, got %s", cfg.Port)
	}
	if cfg.AuthEnabled != false {
		t.Errorf("expected default AuthEnabled false, got %v", cfg.AuthEnabled)
	}
	if cfg.JWTAlgorithm != "HS256" {
		t.Errorf("expected default JWTAlgorithm HS256, got %s", cfg.JWTAlgorithm)
	}
	if cfg.JWTExpirationSeconds != 3600 {
		t.Errorf("expected default JWTExpirationSeconds 3600, got %d", cfg.JWTExpirationSeconds)
	}
}

func TestLoad_ReadsEnvVarsWhenSet(t *testing.T) {
	os.Setenv("PORT", "9090")
	os.Setenv("AUTH_ENABLED", "true")
	os.Setenv("IDENTITY_SERVICE_URL", "http://identity:8000")
	os.Setenv("JWT_ALGORITHM", "RS256")
	os.Setenv("JWT_EXPIRATION", "7200")
	defer func() {
		os.Unsetenv("PORT")
		os.Unsetenv("AUTH_ENABLED")
		os.Unsetenv("IDENTITY_SERVICE_URL")
		os.Unsetenv("JWT_ALGORITHM")
		os.Unsetenv("JWT_EXPIRATION")
	}()

	cfg := Load()

	if cfg.Port != "9090" {
		t.Errorf("expected Port 9090, got %s", cfg.Port)
	}
	if cfg.AuthEnabled != true {
		t.Errorf("expected AuthEnabled true, got %v", cfg.AuthEnabled)
	}
	if cfg.IdentityServiceURL != "http://identity:8000" {
		t.Errorf("expected IdentityServiceURL http://identity:8000, got %s", cfg.IdentityServiceURL)
	}
	if cfg.JWTAlgorithm != "RS256" {
		t.Errorf("expected JWTAlgorithm RS256, got %s", cfg.JWTAlgorithm)
	}
	if cfg.JWTExpirationSeconds != 7200 {
		t.Errorf("expected JWTExpirationSeconds 7200, got %d", cfg.JWTExpirationSeconds)
	}
}

func TestLoad_FallsBackOnInvalidBool(t *testing.T) {
	os.Setenv("AUTH_ENABLED", "not-a-bool")
	defer os.Unsetenv("AUTH_ENABLED")

	cfg := Load()

	if cfg.AuthEnabled != false {
		t.Errorf("expected fallback to default false on invalid bool, got %v", cfg.AuthEnabled)
	}
}

func TestLoad_FallsBackOnInvalidInt(t *testing.T) {
	os.Setenv("JWT_EXPIRATION", "not-a-number")
	defer os.Unsetenv("JWT_EXPIRATION")

	cfg := Load()

	if cfg.JWTExpirationSeconds != 3600 {
		t.Errorf("expected fallback to default 3600 on invalid int, got %d", cfg.JWTExpirationSeconds)
	}
}
