package authorization

import "net/http"

type RoutePermission struct {
	Method string
	Prefix string
	Scope  string
}

var ProtectedRoutes = []RoutePermission{

	//ORGANIZATIONS

	{
		Method: http.MethodGet,
		Prefix: "/api/v1/organizations",
		Scope:  "organization:read",
	},

	{
		Method: http.MethodPost,
		Prefix: "/api/v1/organizations",
		Scope:  "organization:create",
	},

	{
		Method: http.MethodPut,
		Prefix: "/api/v1/organizations",
		Scope:  "organization:update",
	},

	{
		Method: http.MethodDelete,
		Prefix: "/api/v1/organizations",
		Scope:  "organization:delete",
	},

	// POLICIES

	{
		Method: http.MethodGet,
		Prefix: "/api/v1/policies",
		Scope:  "policy:read",
	},

	{
		Method: http.MethodPost,
		Prefix: "/api/v1/policies",
		Scope:  "policy:create",
	},

	//CONFIGURATION

	{
		Method: http.MethodGet,
		Prefix: "/api/v1/configuration",
		Scope:  "policy:read",
	},

	{
		Method: http.MethodPut,
		Prefix: "/api/v1/configuration",
		Scope:  "configuration:update",
	},

	//AUDIT
	{
		Method: http.MethodGet,
		Prefix: "/api/v1/audit",
		Scope:  "audit:read",
	},

	//SECRETS

	{
		Method: http.MethodGet,
		Prefix: "/api/v1/secret",
		Scope:  "secret:read",
	},

	{
		Method: http.MethodPut,
		Prefix: "/api/v1/secrets",
		Scope:  "secret:update",
	},
}
