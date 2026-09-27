import sqlite3


DATABASE_PATH = "aura.db"


def column_exists(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
) -> bool:
    columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column[1] == column_name
        for column in columns
    )


def run_migration() -> None:
    conn = sqlite3.connect(DATABASE_PATH)

    try:
        if not column_exists(
            conn,
            "user_profiles",
            "generated_from_executions",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN generated_from_executions INTEGER
                NOT NULL DEFAULT 0
                """
            )

        if not column_exists(
            conn,
            "user_profiles",
            "confidence",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN confidence REAL
                NOT NULL DEFAULT 0.0
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()