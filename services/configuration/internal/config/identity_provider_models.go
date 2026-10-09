package config

// ProviderType defines supported identity provider types
type ProviderType string

const (
	ProviderTypeOIDC   ProviderType = "oidc"
	ProviderTypeOAuth2 ProviderType = "oauth2"
	ProviderTypeSAML   ProviderType = "saml"
)

// IsValid checks if provider type is valid
func (pt ProviderType) IsValid() bool {
	return pt == ProviderTypeOIDC || pt == ProviderTypeOAuth2 || pt == ProviderTypeSAML
}

// ProviderConfig struct (matches Bhukailash's definition)
type ProviderConfig struct {
	Type             string   `json:"type"`
	Name             string   `json:"name,omitempty"`
	Enabled          bool     `json:"enabled"`
	IssuerURL        string   `json:"issuer_url,omitempty"`
	AuthorizationURL string   `json:"authorization_url,omitempty"`
	TokenURL         string   `json:"token_url,omitempty"`
	UserinfoURL      string   `json:"userinfo_url,omitempty"`
	JWKSURL          string   `json:"jwks_url,omitempty"`
	ClientID         string   `json:"client_id,omitempty"`
	ClientSecretRef  string   `json:"client_secret_ref,omitempty"`
	Scopes           []string `json:"scopes,omitempty"`
	EntityID         string   `json:"entity_id,omitempty"`
	SSOURL           string   `json:"sso_url,omitempty"`
	Certificate      string   `json:"certificate,omitempty"`
	MetadataURL      string   `json:"metadata_url,omitempty"`
	SigningKeyRef    string   `json:"signing_key_ref,omitempty"`
}
