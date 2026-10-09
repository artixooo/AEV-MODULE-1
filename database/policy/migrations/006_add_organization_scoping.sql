-- Week 4 (#93): add optional organization scoping to roles.
--
-- organization_id is NULL for global/system roles (existing Week 3
-- roles remain unaffected and continue to work across all
-- organizations). A non-NULL value scopes the role to exactly one
-- organization.
--
-- The single-column UNIQUE constraint on role_code is replaced with a
-- composite constraint on (role_code, organization_id), so the same
-- role_code (e.g. "admin") can exist independently within multiple
-- organizations without colliding.
--
-- Known limitation: standard SQL (including Postgres) treats NULL as
-- distinct from itself in composite unique constraints, so this does
-- NOT prevent two different global (organization_id IS NULL) roles
-- from sharing a role_code. If that guarantee is needed, add a
-- partial unique index in a follow-up migration:
--   CREATE UNIQUE INDEX uq_role_code_global ON roles(role_code) WHERE organization_id IS NULL;

-- Find and drop the existing single-column UNIQUE constraint on
-- role_code dynamically, rather than assuming its auto-generated name
-- (avoids silently leaving the old restrictive constraint in place if
-- the name doesn't match what we expect).
DO $$
DECLARE
    existing_constraint text;
BEGIN
    SELECT con.conname INTO existing_constraint
    FROM pg_constraint con
    JOIN pg_class rel ON rel.oid = con.conrelid
    WHERE rel.relname = 'roles'
      AND con.contype = 'u'
      AND array_length(con.conkey, 1) = 1
      AND con.conkey[1] = (
          SELECT attnum FROM pg_attribute
          WHERE attrelid = rel.oid AND attname = 'role_code'
      );

    IF existing_constraint IS NOT NULL THEN
        EXECUTE format('ALTER TABLE roles DROP CONSTRAINT %I', existing_constraint);
    END IF;
END $$;

ALTER TABLE roles
    ADD COLUMN organization_id UUID NULL;

CREATE INDEX idx_roles_organization_id ON roles(organization_id);

ALTER TABLE roles
    ADD CONSTRAINT uq_role_code_organization
        UNIQUE (role_code, organization_id);