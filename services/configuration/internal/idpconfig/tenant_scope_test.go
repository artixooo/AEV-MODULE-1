package idpconfig

import "testing"

func TestConfigKeyForOrg_BuildsExpectedKey(t *testing.T) {
	key, err := ConfigKeyForOrg("org-123")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := "identity_provider:org-123"
	if key != want {
		t.Fatalf("expected key %q, got %q", want, key)
	}
}

func TestConfigKeyForOrg_DifferentOrgsProduceDifferentKeys(t *testing.T) {
	keyA, _ := ConfigKeyForOrg("org-123")
	keyB, _ := ConfigKeyForOrg("org-456")
	if keyA == keyB {
		t.Fatalf("expected different orgs to produce different keys, both got %q", keyA)
	}
}

func TestConfigKeyForOrg_RejectsEmptyOrgID(t *testing.T) {
	_, err := ConfigKeyForOrg("")
	if err == nil {
		t.Fatal("expected an error for empty organizationID")
	}
}
