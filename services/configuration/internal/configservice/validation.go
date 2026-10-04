package configservice

import (
	"errors"
	"fmt"
	"strings"

	"github.com/google/uuid"

	"configuration/internal/repository"
	"configuration/internal/validation"
)

var ErrInvalidConfig = errors.New("configservice: invalid configuration")

// ValidateConfigInput checks structural requirements and the
// secrets-delegation boundary before a configuration entry is created
// or updated.
func ValidateConfigInput(input repository.SaveConfigInput) error {
	if strings.TrimSpace(input.ConfigKey) == "" {
		return fmt.Errorf("%w: config_key is required", ErrInvalidConfig)
	}
	if strings.TrimSpace(input.ConfigValue) == "" {
		return fmt.Errorf("%w: config_value is required", ErrInvalidConfig)
	}
	if input.DataType == "" {
		return fmt.Errorf("%w: data_type is required", ErrInvalidConfig)
	}

	validTypes := map[repository.DataType]bool{
		repository.DataTypeString: true,
		repository.DataTypeInt:    true,
		repository.DataTypeFloat:  true,
		repository.DataTypeBool:   true,
		repository.DataTypeJSON:   true,
	}
	if !validTypes[input.DataType] {
		return fmt.Errorf("%w: unrecognized data_type %q", ErrInvalidConfig, input.DataType)
	}

	if input.OrganizationID != nil {
		if _, err := uuid.Parse(*input.OrganizationID); err != nil {
			return fmt.Errorf("%w: organization_id must be a valid UUID", ErrInvalidConfig)
		}
	}

	// Secrets must be delegated to Vault — reuses the same sensitive-
	// field detection already proven in internal/validation (Week 4/5).
	if validation.IsSensitiveField(input.ConfigKey) {
		return fmt.Errorf("%w: config_key %q looks like a secret name; store a *_ref pointer to Secrets Service instead", ErrInvalidConfig, input.ConfigKey)
	}

	return nil
}
