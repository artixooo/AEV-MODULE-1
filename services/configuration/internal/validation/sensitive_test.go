package validation

import "testing"

func TestIsSensitiveField_DetectsKnownSensitiveNames(t *testing.T) {
	cases := []string{
		"client_secret", "clientSecret",
		"api_key", "apiKey",
		"secret", "password",
		"private_key", "privateKey",
		"signing_key", "signingKey",
		"access_token", "accessToken",
		"refresh_token", "refreshToken",
		"scim_token", "scimToken",
	}
	for _, field := range cases {
		if !IsSensitiveField(field) {
			t.Errorf("expected %q to be detected as sensitive", field)
		}
	}
}

func TestIsSensitiveField_AllowsSafeFields(t *testing.T) {
	safe := []string{
		"client_id", "issuer_url", "authorization_url", "token_url",
		"client_secret_ref", "api_key_ref", "scopes", "enabled",
		"organization_id", "provider_type",
	}
	for _, field := range safe {
		if IsSensitiveField(field) {
			t.Errorf("expected %q to NOT be flagged as sensitive", field)
		}
	}
}

func TestValidateNoSensitiveFields_RejectsRawSecret(t *testing.T) {
	fields := map[string]string{
		"client_id":     "abc123",
		"client_secret": "super-secret-value",
	}
	err := ValidateNoSensitiveFields(fields)
	if err == nil {
		t.Fatal("expected an error for a raw client_secret field")
	}
}

func TestValidateNoSensitiveFields_AllowsRefField(t *testing.T) {
	fields := map[string]string{
		"client_id":         "abc123",
		"client_secret_ref": "secret://identity/org-123/client-secret",
	}
	err := ValidateNoSensitiveFields(fields)
	if err != nil {
		t.Fatalf("expected no error for a *_ref field, got: %v", err)
	}
}

func TestValidateNoSensitiveFields_NoFieldsIsValid(t *testing.T) {
	if err := ValidateNoSensitiveFields(map[string]string{}); err != nil {
		t.Fatalf("expected no error for empty fields, got: %v", err)
	}
}
