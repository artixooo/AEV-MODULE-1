// Package idpconfig provides tenant-scoped access helpers for
// identity-provider configuration, built on top of the existing
// Configuration table rather than a new dedicated table (per Week 4
// design decision — see docs/config_identity-provider.md, Section 15).
package idpconfig

import "fmt"

// configKeyPrefix namespaces identity-provider config keys so they
// don't collide with other configuration entries that might use
// similarly-named keys.
const configKeyPrefix = "identity_provider"

// ConfigKeyForOrg builds the globally-unique config_key used to store
// one organization's identity-provider configuration.
//
// config_key is globally unique in the configuration table (not unique
// per-organization), so tenant isolation for this key is achieved by
// encoding the organization_id directly into the key itself.
func ConfigKeyForOrg(organizationID string) (string, error) {
	if organizationID == "" {
		return "", fmt.Errorf("idpconfig: organizationID is required")
	}
	return fmt.Sprintf("%s:%s", configKeyPrefix, organizationID), nil
}
