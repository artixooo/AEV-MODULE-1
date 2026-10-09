package hashchain

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// GenesisHash represents the initial zero-hash block
const GenesisHash = "0000000000000000000000000000000000000000000000000000000000000000"

// AuditEntry is a minimal payload used for canonical hashing
type AuditEntry struct {
	Action    string `json:"action"`
	Actor     string `json:"actor"`
	Service   string `json:"service"`
	Status    string `json:"status"`
	Timestamp string `json:"timestamp"`
}

// VerificationResult contains the cryptographic chain validation report
type VerificationResult struct {
	Valid          bool      `json:"valid"`
	ChainLength    int       `json:"chain_length"`
	GenesisHash    string    `json:"genesis_hash"`
	TipHash        string    `json:"tip_hash"`
	BrokenAtIndex  int       `json:"broken_at_index,omitempty"`
	BrokenRecordID string    `json:"broken_record_id,omitempty"`
	ErrorMessage   string    `json:"error_message,omitempty"`
	VerifiedAt     time.Time `json:"verified_at"`
}

// ComputeHash calculates the SHA-256 hash linking the previous hash with canonical JSON payload
func ComputeHash(prevHash string, entry AuditEntry) (string, error) {
	canonical, err := json.Marshal(entry)
	if err != nil {
		return "", fmt.Errorf("canonical json marshal failed: %w", err)
	}

	payload := fmt.Sprintf("%s:%s", prevHash, string(canonical))
	sum := sha256.Sum256([]byte(payload))
	return hex.EncodeToString(sum[:]), nil
}

// VerifyLedger reads the database audit chain and validates cryptographic integrity
func VerifyLedger(ctx context.Context, db *pgxpool.Pool) (VerificationResult, error) {
	query := `
		SELECT 
			l.id::text, 
			l.action, 
			COALESCE(l.actor_name, 'unknown'), 
			l.service_name, 
			l.status, 
			to_char(l.event_timestamp AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as ts,
			h.previous_hash, 
			h.current_hash
		FROM audit_logs l
		JOIN audit_hash_chain h ON l.id = h.audit_log_id
		ORDER BY l.event_timestamp ASC, l.created_at ASC
	`

	rows, err := db.Query(ctx, query)
	if err != nil {
		return VerificationResult{
			Valid:        false,
			ErrorMessage: fmt.Sprintf("database query failed: %v", err),
			VerifiedAt:   time.Now().UTC(),
		}, err
	}
	defer rows.Close()

	expectedPrev := GenesisHash
	tipHash := GenesisHash
	index := 0

	for rows.Next() {
		index++
		var id, action, actor, service, status, ts, prevHash, currHash string
		if err := rows.Scan(&id, &action, &actor, &service, &status, &ts, &prevHash, &currHash); err != nil {
			return VerificationResult{
				Valid:        false,
				ErrorMessage: fmt.Sprintf("row scan failed at %d: %v", index, err),
				VerifiedAt:   time.Now().UTC(),
			}, err
		}

		if prevHash != expectedPrev {
			return VerificationResult{
				Valid:          false,
				ChainLength:    index,
				BrokenAtIndex:  index,
				BrokenRecordID: id,
				ErrorMessage:   fmt.Sprintf("Previous hash mismatch at step %d: expected %s, found %s", index, expectedPrev, prevHash),
				VerifiedAt:     time.Now().UTC(),
			}, nil
		}

		entry := AuditEntry{
			Action:    action,
			Actor:     actor,
			Service:   service,
			Status:    status,
			Timestamp: ts,
		}

		computed, err := ComputeHash(prevHash, entry)
		if err != nil {
			return VerificationResult{
				Valid:          false,
				ChainLength:    index,
				BrokenAtIndex:  index,
				BrokenRecordID: id,
				ErrorMessage:   fmt.Sprintf("Hash computation failed at step %d: %v", index, err),
				VerifiedAt:     time.Now().UTC(),
			}, nil
		}

		if computed != currHash {
			return VerificationResult{
				Valid:          false,
				ChainLength:    index,
				BrokenAtIndex:  index,
				BrokenRecordID: id,
				ErrorMessage:   fmt.Sprintf("Mathematical tamper detected at step %d (ID %s): computed hash %s != recorded hash %s", index, id, computed, currHash),
				VerifiedAt:     time.Now().UTC(),
			}, nil
		}

		expectedPrev = currHash
		tipHash = currHash
	}

	return VerificationResult{
		Valid:       true,
		ChainLength: index,
		GenesisHash: GenesisHash,
		TipHash:     tipHash,
		VerifiedAt:  time.Now().UTC(),
	}, nil
}
