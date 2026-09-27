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
            "study_duration_multiplier",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN study_duration_multiplier REAL
                NOT NULL DEFAULT 1.0
                """
            )

        if not column_exists(
            conn,
            "user_profiles",
            "personal_duration_multiplier",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN personal_duration_multiplier REAL
                NOT NULL DEFAULT 1.0
                """
            )

        if not column_exists(
            conn,
            "user_profiles",
            "health_duration_multiplier",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN health_duration_multiplier REAL
                NOT NULL DEFAULT 1.0
                """
            )

        if not column_exists(
            conn,
            "user_profiles",
            "other_duration_multiplier",
        ):
            conn.execute(
                """
                ALTER TABLE user_profiles
                ADD COLUMN other_duration_multiplier REAL
                NOT NULL DEFAULT 1.0
                """
            )

        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()