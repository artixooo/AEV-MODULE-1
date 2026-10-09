package models

// Authentication event types.
const (
	EventTypeUserRegistered = "user.registered"
	EventTypeUserLogin      = "user.login"
	EventTypeUserLogout     = "user.logout"
	EventTypeTokenRefreshed = "token.refreshed"
	EventTypeMFAVerified    = "mfa.verified"
)

// Organization event types.
const (
	EventTypeOrganizationCreated = "organization.created"
	EventTypeOrganizationUpdated = "organization.updated"
	EventTypeOrganizationDeleted = "organization.deleted"
)

// Membership event types.
const (
	EventTypeMembershipCreated = "membership.created"
	EventTypeMembershipUpdated = "membership.updated"
	EventTypeMembershipDeleted = "membership.deleted"
)

// Workspace event types.
const (
	EventTypeWorkspaceCreated = "workspace.created"
	EventTypeWorkspaceUpdated = "workspace.updated"
	EventTypeWorkspaceDeleted = "workspace.deleted"
)

// Project event types.
const (
	EventTypeProjectCreated = "project.created"
	EventTypeProjectUpdated = "project.updated"
	EventTypeProjectDeleted = "project.deleted"
)
