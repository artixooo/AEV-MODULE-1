package repository

import (
	"context"
	"errors"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// PostgresRepository implements Repository against configuration_db,
// using the approved 3-table schema (configuration, feature_flags,
// configuration_history).
type PostgresRepository struct {
	db *pgxpool.Pool
}

// NewPostgresRepository builds a repository from an existing pgx pool.
// Callers own the pool's lifecycle (create it at startup, Close() it on
// shutdown).
func NewPostgresRepository(db *pgxpool.Pool) *PostgresRepository {
	return &PostgresRepository{db: db}
}

var _ Repository = (*PostgresRepository)(nil) // compile-time interface check

const configColumns = `
	id::text, config_key, config_value, data_type, scope,
	organization_id::text, workspace_id::text, project_id::text,
	description, is_editable, created_at, updated_at
`

func scanConfiguration(row pgx.Row) (*Configuration, error) {
	var c Configuration
	var dataType, scope string
	err := row.Scan(
		&c.ID, &c.ConfigKey, &c.ConfigValue, &dataType, &scope,
		&c.OrganizationID, &c.WorkspaceID, &c.ProjectID,
		&c.Description, &c.IsEditable, &c.CreatedAt, &c.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}
	c.DataType = DataType(dataType)
	c.Scope = Scope(scope)
	return &c, nil
}

// ---- Configuration -------------------------------------------------------

func (r *PostgresRepository) GetConfig(ctx context.Context, key string) (*Configuration, error) {
	q := fmt.Sprintf(`SELECT %s FROM configuration WHERE config_key = $1`, configColumns)

	c, err := scanConfiguration(r.db.QueryRow(ctx, q, key))
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return c, nil
}

// SaveConfig creates or updates a configuration row, keyed on config_key.
// Every call also writes a row to configuration_history recording the
// old and new value, so this always runs inside a transaction.
func (r *PostgresRepository) SaveConfig(ctx context.Context, input SaveConfigInput) (*Configuration, error) {
	if input.ConfigKey == "" {
		return nil, fmt.Errorf("%w: config_key is required", ErrInvalidInput)
	}

	tx, err := r.db.Begin(ctx)
	if err != nil {
		return nil, err
	}
	defer tx.Rollback(ctx) // no-op if committed

	// Look up the existing row (if any) so we know the old value for the
	// history entry, and lock it for update to avoid a race with a
	// concurrent writer.
	var existingID string
	var oldValue string
	err = tx.QueryRow(ctx,
		`SELECT id::text, config_value FROM configuration WHERE config_key = $1 FOR UPDATE`,
		input.ConfigKey,
	).Scan(&existingID, &oldValue)

	var saved *Configuration

	switch {
	case errors.Is(err, pgx.ErrNoRows):
		// New key — insert it.
		insertQ := fmt.Sprintf(`
			INSERT INTO configuration (
				config_key, config_value, data_type, scope,
				organization_id, workspace_id, project_id,
				description, is_editable
			)
			VALUES ($1, $2, $3, $4, $5::uuid, $6::uuid, $7::uuid, $8, $9)
			RETURNING %s
		`, configColumns)

		saved, err = scanConfiguration(tx.QueryRow(ctx, insertQ,
			input.ConfigKey, input.ConfigValue, string(input.DataType), string(input.Scope),
			input.OrganizationID, input.WorkspaceID, input.ProjectID,
			input.Description, input.IsEditable,
		))
		if err != nil {
			return nil, err
		}

		if err := insertHistory(ctx, tx, saved.ID, nil, input.ConfigValue, input.ChangedBy, input.ChangeReason); err != nil {
			return nil, err
		}

	case err != nil:
		return nil, err

	default:
		// Existing key — update it.
		updateQ := fmt.Sprintf(`
			UPDATE configuration SET
				config_value = $2, data_type = $3, scope = $4,
				organization_id = $5::uuid, workspace_id = $6::uuid, project_id = $7::uuid,
				description = $8, is_editable = $9, updated_at = CURRENT_TIMESTAMP
			WHERE id = $1
			RETURNING %s
		`, configColumns)

		saved, err = scanConfiguration(tx.QueryRow(ctx, updateQ,
			existingID, input.ConfigValue, string(input.DataType), string(input.Scope),
			input.OrganizationID, input.WorkspaceID, input.ProjectID,
			input.Description, input.IsEditable,
		))
		if err != nil {
			return nil, err
		}

		oldValueCopy := oldValue
		if err := insertHistory(ctx, tx, saved.ID, &oldValueCopy, input.ConfigValue, input.ChangedBy, input.ChangeReason); err != nil {
			return nil, err
		}
	}

	if err := tx.Commit(ctx); err != nil {
		return nil, err
	}
	return saved, nil
}

func insertHistory(ctx context.Context, tx pgx.Tx, configurationID string, oldValue *string, newValue string, changedBy *string, changeReason string) error {
	_, err := tx.Exec(ctx, `
		INSERT INTO configuration_history (
			configuration_id, old_value, new_value, changed_by, change_reason
		)
		VALUES ($1::uuid, $2, $3, $4::uuid, $5)
	`, configurationID, oldValue, newValue, changedBy, changeReason)
	return err
}

func (r *PostgresRepository) ListConfigurations(ctx context.Context, filter ListFilter) ([]Configuration, error) {
	q := fmt.Sprintf(`
		SELECT %s FROM configuration
		WHERE ($1 = '' OR scope = $1)
		  AND ($2::uuid IS NULL OR organization_id = $2::uuid)
		  AND ($3::uuid IS NULL OR workspace_id = $3::uuid)
		  AND ($4::uuid IS NULL OR project_id = $4::uuid)
		ORDER BY config_key
	`, configColumns)

	rows, err := r.db.Query(ctx, q, string(filter.Scope), filter.OrganizationID, filter.WorkspaceID, filter.ProjectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var configs []Configuration
	for rows.Next() {
		c, err := scanConfiguration(rows)
		if err != nil {
			return nil, err
		}
		configs = append(configs, *c)
	}
	return configs, rows.Err()
}

func (r *PostgresRepository) GetConfigurationHistory(ctx context.Context, configurationID string) ([]ConfigurationHistory, error) {
	const q = `
		SELECT id::text, configuration_id::text, old_value, new_value,
		       changed_by::text, change_reason, changed_at
		FROM configuration_history
		WHERE configuration_id = $1::uuid
		ORDER BY changed_at DESC
	`

	rows, err := r.db.Query(ctx, q, configurationID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var history []ConfigurationHistory
	for rows.Next() {
		var h ConfigurationHistory
		if err := rows.Scan(&h.ID, &h.ConfigurationID, &h.OldValue, &h.NewValue, &h.ChangedBy, &h.ChangeReason, &h.ChangedAt); err != nil {
			return nil, err
		}
		history = append(history, h)
	}
	return history, rows.Err()
}

// ---- Feature flags ---------------------------------------------------------

const featureFlagColumns = `
	id::text, flag_key, flag_name, description, is_enabled, scope,
	organization_id::text, workspace_id::text, project_id::text,
	rollout_percentage, created_at, updated_at
`

func scanFeatureFlag(row pgx.Row) (*FeatureFlag, error) {
	var f FeatureFlag
	var scope string
	err := row.Scan(
		&f.ID, &f.FlagKey, &f.FlagName, &f.Description, &f.IsEnabled, &scope,
		&f.OrganizationID, &f.WorkspaceID, &f.ProjectID,
		&f.RolloutPercentage, &f.CreatedAt, &f.UpdatedAt,
	)
	if err != nil {
		return nil, err
	}
	f.Scope = Scope(scope)
	return &f, nil
}

func (r *PostgresRepository) GetFeatureFlag(ctx context.Context, flagKey string) (*FeatureFlag, error) {
	q := fmt.Sprintf(`SELECT %s FROM feature_flags WHERE flag_key = $1`, featureFlagColumns)

	f, err := scanFeatureFlag(r.db.QueryRow(ctx, q, flagKey))
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, ErrNotFound
	}
	if err != nil {
		return nil, err
	}
	return f, nil
}

func (r *PostgresRepository) SaveFeatureFlag(ctx context.Context, input SaveFeatureFlagInput) (*FeatureFlag, error) {
	if input.FlagKey == "" {
		return nil, fmt.Errorf("%w: flag_key is required", ErrInvalidInput)
	}

	q := fmt.Sprintf(`
		INSERT INTO feature_flags (
			flag_key, flag_name, description, is_enabled, scope,
			organization_id, workspace_id, project_id, rollout_percentage
		)
		VALUES ($1, $2, $3, $4, $5, $6::uuid, $7::uuid, $8::uuid, $9)
		ON CONFLICT (flag_key)
		DO UPDATE SET
			flag_name = EXCLUDED.flag_name,
			description = EXCLUDED.description,
			is_enabled = EXCLUDED.is_enabled,
			scope = EXCLUDED.scope,
			organization_id = EXCLUDED.organization_id,
			workspace_id = EXCLUDED.workspace_id,
			project_id = EXCLUDED.project_id,
			rollout_percentage = EXCLUDED.rollout_percentage,
			updated_at = CURRENT_TIMESTAMP
		RETURNING %s
	`, featureFlagColumns)

	f, err := scanFeatureFlag(r.db.QueryRow(ctx, q,
		input.FlagKey, input.FlagName, input.Description, input.IsEnabled, string(input.Scope),
		input.OrganizationID, input.WorkspaceID, input.ProjectID, input.RolloutPercentage,
	))
	if err != nil {
		return nil, err
	}
	return f, nil
}

func (r *PostgresRepository) ListFeatureFlags(ctx context.Context, filter ListFilter) ([]FeatureFlag, error) {
	q := fmt.Sprintf(`
		SELECT %s FROM feature_flags
		WHERE ($1 = '' OR scope = $1)
		  AND ($2::uuid IS NULL OR organization_id = $2::uuid)
		  AND ($3::uuid IS NULL OR workspace_id = $3::uuid)
		  AND ($4::uuid IS NULL OR project_id = $4::uuid)
		ORDER BY flag_key
	`, featureFlagColumns)

	rows, err := r.db.Query(ctx, q, string(filter.Scope), filter.OrganizationID, filter.WorkspaceID, filter.ProjectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var flags []FeatureFlag
	for rows.Next() {
		f, err := scanFeatureFlag(rows)
		if err != nil {
			return nil, err
		}
		flags = append(flags, *f)
	}
	return flags, rows.Err()
}

// DeleteConfig removes a configuration row by config_key. Writes a final
// audit row to configuration_history recording the deleted value before
// removal, so the history remains a complete record even after deletion.
func (r *PostgresRepository) DeleteConfig(ctx context.Context, key string) error {
	tx, err := r.db.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	var id, oldValue string
	err = tx.QueryRow(ctx,
		`SELECT id::text, config_value FROM configuration WHERE config_key = $1 FOR UPDATE`,
		key,
	).Scan(&id, &oldValue)
	if errors.Is(err, pgx.ErrNoRows) {
		return ErrNotFound
	}
	if err != nil {
		return err
	}

	if err := insertHistory(ctx, tx, id, &oldValue, "", nil, "configuration deleted"); err != nil {
		return err
	}

	if _, err := tx.Exec(ctx, `DELETE FROM configuration WHERE id = $1`, id); err != nil {
		return err
	}

	return tx.Commit(ctx)
}
