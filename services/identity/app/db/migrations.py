from pathlib import Path

from sqlalchemy import text  # type: ignore

from app.core.database import engine


DOCKER_MIGRATIONS_DIR = Path("/app/database/identity/migrations")


def _get_migrations_dir() -> Path:
    if DOCKER_MIGRATIONS_DIR.exists():
        return DOCKER_MIGRATIONS_DIR

    project_root = Path(__file__).resolve().parents[4]
    migrations_dir = project_root / "database" / "identity" / "migrations"

    if migrations_dir.exists():
        return migrations_dir

    raise RuntimeError(
        f"No Identity migration directory found. "
        f"Checked {migrations_dir} and {DOCKER_MIGRATIONS_DIR}"
    )


def run_migrations():
    migrations_dir = _get_migrations_dir()
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        raise RuntimeError(
            f"No migration files found in {migrations_dir}"
        )

    with engine.begin() as connection:
        for migration_file in migration_files:
            print(f"Running migration: {migration_file.name}")

            sql = migration_file.read_text(encoding="utf-8").strip()

            if sql:
                connection.execute(text(sql))

            print(f"Migration completed: {migration_file.name}")

    print("All Identity Service migrations completed successfully.")
