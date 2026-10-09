// Package validation provides shared, reusable checks that don't belong
// to any single domain model — starting with sensitive-field detection
// for identity-provider configuration (Week 4).
package validation

import "strings"

// sensitiveFieldNames lists field names that must never be accepted as
// raw values in configuration input. Comparison is case-insensitive and
// ignores common separator styles (snake_case vs camelCase), so a single
// canonical list covers both naming conventions.
var sensitiveFieldNames = map[string]bool{
	"clientsecret": true,
	"apikey":       true,
	"secret":       true,
	"password":     true,
	"privatekey":   true,
	"signingkey":   true,
	"accesstoken":  true,
	"refreshtoken": true,
	"scimtoken":    true,
}

// normalize strips underscores and lowercases a field name, so
// "client_secret" and "clientSecret" both normalize to "clientsecret".
func normalize(field string) string {
	return strings.ToLower(strings.ReplaceAll(field, "_", ""))
}

// IsSensitiveField reports whether the given field name is considered
// sensitive and must never be stored directly by the Configuration
// Service (it must be delegated to the Secrets Service via a *_ref
// field instead).
func IsSensitiveField(field string) bool {
	return sensitiveFieldNames[normalize(field)]
}

// ValidateNoSensitiveFields checks a set of input field names and
// returns an error naming the first sensitive field found, or nil if
// none are present. fields is typically a map of field name -> raw
// value decoded from a request body.
func ValidateNoSensitiveFields(fields map[string]string) error {
	for name := range fields {
		if IsSensitiveField(name) {
			return &SensitiveFieldError{Field: name}
		}
	}
	return nil
}

// SensitiveFieldError indicates a request attempted to submit a raw
// sensitive value directly, instead of a *_ref placeholder.
type SensitiveFieldError struct {
	Field string
}

func (e *SensitiveFieldError) Error() string {
	return "validation: field \"" + e.Field + "\" must not be stored directly; use a *_ref field pointing to the Secrets Service instead"
}
