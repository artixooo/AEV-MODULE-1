package configservice

import "context"

// Action identifies what kind of operation is being authorized or
// audited.
type Action string

const (
	ActionCreate Action = "create"
	ActionRead   Action = "read"
	ActionUpdate Action = "update"
	ActionDelete Action = "delete"
)

// Authorizer checks whether an actor may perform an action against a
// given config key. The real implementation calls Policy Service, per
// the Week 6 "Integrate Policy authorization" task — that integration
// is a dependency on Week 5's Policy/authorization framework, which
// isn't confirmed yet, so this package only defines the contract here.
// Do not build the real Policy HTTP/gRPC client against guessed
// endpoints — confirm the actual contract first, same lesson as Week 4.
type Authorizer interface {
	Authorize(ctx context.Context, actor Actor, action Action, configKey string) (bool, error)
}

// NoopAuthorizer allows every action. Used only as a safe default so
// this package compiles and is unit-testable before a real Policy
// Service client exists. MUST be replaced before production use.
type NoopAuthorizer struct{}

func (NoopAuthorizer) Authorize(ctx context.Context, actor Actor, action Action, configKey string) (bool, error) {
	return true, nil
}

// DenyAllAuthorizer rejects every action. Useful in tests to prove
// authorization is actually being checked, not bypassed.
type DenyAllAuthorizer struct{}

func (DenyAllAuthorizer) Authorize(ctx context.Context, actor Actor, action Action, configKey string) (bool, error) {
	return false, nil
}

// AuditEvent captures one configuration change for the Audit contract.
type AuditEvent struct {
	Action    Action
	Actor     Actor
	ConfigKey string
	OldValue  string
	NewValue  string
}

// Auditor records configuration changes through the Audit contract. The
// real implementation publishes to Audit Service (per the Week 6
// "Audit configuration changes through the Audit contract" task and the
// "Audit event contracts" dependency) — that contract isn't confirmed
// yet either, so this stays an interface until it is.
type Auditor interface {
	RecordConfigChange(ctx context.Context, event AuditEvent)
}

// NoopAuditor records nothing. Safe default until the real Audit
// contract is wired in.
type NoopAuditor struct{}

func (NoopAuditor) RecordConfigChange(ctx context.Context, event AuditEvent) {}

// RecordingAuditor collects events in memory — useful for tests that
// need to assert an audit event was actually recorded.
type RecordingAuditor struct {
	Events []AuditEvent
}

func (r *RecordingAuditor) RecordConfigChange(ctx context.Context, event AuditEvent) {
	r.Events = append(r.Events, event)
}
