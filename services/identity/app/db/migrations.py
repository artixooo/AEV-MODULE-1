from pathlib import Path

from sqlalchemy import text # type: ignore

from app.core.database import engine


MIGRATIONS_DIR = Path("/app/database/identity/migrations")


def run_migrations():
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        raise RuntimeError(
            f"No migration files found in {MIGRATIONS_DIR}"
        )

    with engine.begin() as connection:
        for migration_file in migration_files:
            print(f"Running migration: {migration_file.name}")

            sql = migration_file.read_text(encoding="utf-8").strip()

            if sql:
                connection.execute(text(sql))

            print(f"Migration completed: {migration_file.name}")

    print("All Identity Service migrations completed successfully.")