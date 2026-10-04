package configservice

import (
	"context"
	"os"
	"testing"

	"github.com/jackc/pgx/v5/pgxpool"

	"configuration/internal/repository"
)

func newTestRepository(t *testing.T) repository.Repository {
	t.Helper()
	dsn := os.Getenv("DATABASE_URL")
	if dsn == "" {
		t.Skip("DATABASE_URL not set, skipping configservice tests")
	}
	pool, err := pgxpool.New(context.Background(), dsn)
	if err != nil {
		t.Fatalf("failed to create pgx pool: %v", err)
	}
	t.Cleanup(func() {
		pool.Close()
	})
	return repository.NewPostgresRepository(pool)
}

func testInput(key, orgID string) repository.SaveConfigInput {
	return repository.SaveConfigInput{
		ConfigKey:      key,
		ConfigValue:    "some-value",
		DataType:       repository.DataTypeString,
		Scope:          repository.ScopeOrganization,
		OrganizationID: &orgID,
		IsEditable:     true,
	}
}

func TestCreate_InsertsNewConfig(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000001"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	saved, err := svc.Create(ctx, actor, testInput("week6_test_create_key", orgID))
	if err != nil {
		t.Fatalf("expected Create to succeed, got: %v", err)
	}
	if saved.ConfigValue != "some-value" {
		t.Fatalf("expected value 'some-value', got %q", saved.ConfigValue)
	}
}

func TestCreate_RejectsDuplicateKey(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000002"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	input := testInput("week6_test_dup_key", orgID)
	if _, err := svc.Create(ctx, actor, input); err != nil {
		t.Fatalf("expected first Create to succeed, got: %v", err)
	}

	_, err := svc.Create(ctx, actor, input)
	if err != ErrAlreadyExists {
		t.Fatalf("expected ErrAlreadyExists on duplicate Create, got: %v", err)
	}
}

func TestUpdate_FailsForNonExistentKey(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000003"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	_, err := svc.Update(ctx, actor, testInput("week6_test_never_created", orgID))
	if err != repository.ErrNotFound {
		t.Fatalf("expected ErrNotFound updating a key that was never created, got: %v", err)
	}
}

func TestUpdate_ChangesExistingValueAndAudits(t *testing.T) {
	repo := newTestRepository(t)
	auditor := &RecordingAuditor{}
	svc := New(repo, nil, auditor)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000004"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	input := testInput("week6_test_update_key", orgID)
	if _, err := svc.Create(ctx, actor, input); err != nil {
		t.Fatalf("expected Create to succeed, got: %v", err)
	}

	input.ConfigValue = "updated-value"
	saved, err := svc.Update(ctx, actor, input)
	if err != nil {
		t.Fatalf("expected Update to succeed, got: %v", err)
	}
	if saved.ConfigValue != "updated-value" {
		t.Fatalf("expected updated value, got %q", saved.ConfigValue)
	}

	if len(auditor.Events) != 2 {
		t.Fatalf("expected 2 audit events (create + update), got %d", len(auditor.Events))
	}
	if auditor.Events[1].Action != ActionUpdate {
		t.Fatalf("expected second audit event to be an update, got %v", auditor.Events[1].Action)
	}
}

func TestDelete_RemovesConfigAndAudits(t *testing.T) {
	repo := newTestRepository(t)
	auditor := &RecordingAuditor{}
	svc := New(repo, nil, auditor)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000005"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	input := testInput("week6_test_delete_key", orgID)
	if _, err := svc.Create(ctx, actor, input); err != nil {
		t.Fatalf("expected Create to succeed, got: %v", err)
	}

	if err := svc.Delete(ctx, actor, input.ConfigKey); err != nil {
		t.Fatalf("expected Delete to succeed, got: %v", err)
	}

	_, err := svc.Get(ctx, actor, input.ConfigKey)
	if err != repository.ErrNotFound {
		t.Fatalf("expected ErrNotFound after Delete, got: %v", err)
	}

	found := false
	for _, e := range auditor.Events {
		if e.Action == ActionDelete {
			found = true
		}
	}
	if !found {
		t.Fatal("expected a delete audit event to be recorded")
	}
}

func TestCrossTenantIsolation_CannotReadOtherOrgsConfig(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()

	orgA := "d0d0d0d0-0000-0000-0000-00000000000a"
	orgB := "d0d0d0d0-0000-0000-0000-00000000000b"
	actorA := Actor{UserID: "user-a", OrganizationID: orgA}
	actorB := Actor{UserID: "user-b", OrganizationID: orgB}

	input := testInput("week6_test_isolation_key", orgA)
	if _, err := svc.Create(ctx, actorA, input); err != nil {
		t.Fatalf("expected org A Create to succeed, got: %v", err)
	}

	_, err := svc.Get(ctx, actorB, input.ConfigKey)
	if err != ErrUnauthorized {
		t.Fatalf("expected ErrUnauthorized when org B reads org A's config, got: %v", err)
	}
}

func TestCrossTenantIsolation_CannotUpdateOtherOrgsConfig(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()

	orgA := "d0d0d0d0-0000-0000-0000-00000000000c"
	orgB := "d0d0d0d0-0000-0000-0000-00000000000d"
	actorA := Actor{UserID: "user-a", OrganizationID: orgA}
	actorB := Actor{UserID: "user-b", OrganizationID: orgB}

	input := testInput("week6_test_isolation_update_key", orgA)
	if _, err := svc.Create(ctx, actorA, input); err != nil {
		t.Fatalf("expected org A Create to succeed, got: %v", err)
	}

	attempt := input
	attempt.OrganizationID = &orgB
	_, err := svc.Update(ctx, actorB, attempt)
	if err != ErrUnauthorized {
		t.Fatalf("expected ErrUnauthorized when org B updates org A's config, got: %v", err)
	}
}

func TestAuthorization_DenyAllAuthorizerBlocksEverything(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, DenyAllAuthorizer{}, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-00000000000e"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	_, err := svc.Create(ctx, actor, testInput("week6_test_denied_key", orgID))
	if err != ErrUnauthorized {
		t.Fatalf("expected ErrUnauthorized with DenyAllAuthorizer, got: %v", err)
	}
}

func TestValidateConfigInput_RejectsSensitiveFieldName(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-00000000000f"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	input := testInput("client_secret", orgID) // config_key itself looks like a secret name
	_, err := svc.Create(ctx, actor, input)
	if err == nil {
		t.Fatal("expected an error for a config_key resembling a sensitive field name")
	}
}

func TestVersions_ReturnsHistoryAfterUpdates(t *testing.T) {
	repo := newTestRepository(t)
	svc := New(repo, nil, nil)
	ctx := context.Background()
	orgID := "d0d0d0d0-0000-0000-0000-000000000010"
	actor := Actor{UserID: "user-1", OrganizationID: orgID}

	input := testInput("week6_test_versions_key", orgID)
	saved, err := svc.Create(ctx, actor, input)
	if err != nil {
		t.Fatalf("expected Create to succeed, got: %v", err)
	}

	input.ConfigValue = "second-value"
	if _, err := svc.Update(ctx, actor, input); err != nil {
		t.Fatalf("expected Update to succeed, got: %v", err)
	}

	history, err := svc.Versions(ctx, actor, saved.ID)
	if err != nil {
		t.Fatalf("expected Versions to succeed, got: %v", err)
	}
	if len(history) != 2 {
		t.Fatalf("expected 2 history entries (create + update), got %d", len(history))
	}
}
