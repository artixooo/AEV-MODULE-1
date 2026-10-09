package handlers

import (
	"context"
	"encoding/json"
	"net/http"
	"time"

	"audit/internal/hashchain"
	"github.com/jackc/pgx/v5/pgxpool"
)

type AuditLogRecord struct {
	ID           string    `json:"id"`
	Action       string    `json:"action"`
	ActorName    string    `json:"actor_name"`
	ServiceName  string    `json:"service_name"`
	Status       string    `json:"status"`
	PreviousHash string    `json:"previous_hash"`
	CurrentHash  string    `json:"current_hash"`
	Timestamp    time.Time `json:"timestamp"`
}

func LedgerHandler(db *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
		defer cancel()

		query := `
			SELECT 
				l.id::text, 
				l.action, 
				COALESCE(l.actor_name, 'unknown'), 
				l.service_name, 
				l.status, 
				h.previous_hash, 
				h.current_hash,
				l.event_timestamp
			FROM audit_logs l
			JOIN audit_hash_chain h ON l.id = h.audit_log_id
			ORDER BY l.event_timestamp ASC
			LIMIT 100
		`

		rows, err := db.Query(ctx, query)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer rows.Close()

		var records []AuditLogRecord
		for rows.Next() {
			var rec AuditLogRecord
			if err := rows.Scan(
				&rec.ID,
				&rec.Action,
				&rec.ActorName,
				&rec.ServiceName,
				&rec.Status,
				&rec.PreviousHash,
				&rec.CurrentHash,
				&rec.Timestamp,
			); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
			records = append(records, rec)
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(map[string]interface{}{
			"records": records,
			"count":   len(records),
		})
	}
}

func VerifyHandler(db *pgxpool.Pool) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodPost {
			http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
			return
		}

		ctx, cancel := context.WithTimeout(r.Context(), 10*time.Second)
		defer cancel()

		result, err := hashchain.VerifyLedger(ctx, db)
		if err != nil {
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusInternalServerError)
			json.NewEncoder(w).Encode(result)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(result)
	}
}
