package hashchain

import (
	"testing"
)

func TestComputeHashDeterministic(t *testing.T) {
	prev := GenesisHash
	entry := AuditEntry{
		Action:    "SYSTEM_BOOT",
		Actor:     "system",
		Service:   "gateway",
		Status:    "SUCCESS",
		Timestamp: "2026-10-09T00:00:00Z",
	}

	hash1, err := ComputeHash(prev, entry)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	hash2, err := ComputeHash(prev, entry)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}

	if hash1 != hash2 {
		t.Errorf("expected deterministic hash, got %s and %s", hash1, hash2)
	}

	if len(hash1) != 64 {
		t.Errorf("expected 64 character hex SHA-256 digest, got len %d", len(hash1))
	}
}

func TestTamperDetection(t *testing.T) {
	prev := GenesisHash
	entry := AuditEntry{
		Action:    "USER_LOGIN",
		Actor:     "admin@cyart.io",
		Service:   "identity",
		Status:    "SUCCESS",
		Timestamp: "2026-10-09T00:05:00Z",
	}

	validHash, _ := ComputeHash(prev, entry)

	// Tampered entry (modified actor)
	tamperedEntry := entry
	tamperedEntry.Actor = "attacker@evil.com"
	tamperedHash, _ := ComputeHash(prev, tamperedEntry)

	if validHash == tamperedHash {
		t.Errorf("tampered hash must not match original hash!")
	}
}
